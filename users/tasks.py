from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.task.schedules import crontab
from datetime import timedelta, date, datetime
from django.utils import timezone
from collections import namedtuple
from django.db import transaction

from celery.task import periodic_task

from .models import *
from ocems.settings import conn

import urllib.request
import json
import pytz

#cur = conn.cursor()
		
def getConsumptionStatus(amt):
	if amt > 500:
		return 0
	elif amt <= 500 and amt > 0:
		return 1
	elif amt <= 0 and amt > -200:
		return 2
	else:
		return 3

@periodic_task(run_every=crontab(minute='*/10'))
def ReadEbAndDG():
	print("ReadEbAndDG")
	Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	cur = conn.cursor()
	c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption]")
	c = c.fetchall()
	#c = getFlatData()
	if c:
		l = []
		sms = []
		for i in c:
			cp = Consumptions(*i)
			cons = Consumption.objects.get(flat__id=cp.flat_id)
			da = DeductionAmt.objects.get(tower=cons.flat.tower)
			if cp.eb > cons.getLastEB() or cp.dg > cons.getLastDG():
				consumed = (cp.eb-cons.getLastEB())*float(da.eb_price)+(cp.dg-cons.getLastDG())*float(da.dg_price)
				amt_left = float(cons.amt_left)-consumed
				ng_eb = cp.eb-float(cons.start_eb)
				ng_dg = cp.dg-float(cons.start_dg)
				status = getConsumptionStatus(amt_left)
				dtnow = timezone.localtime(timezone.now())
				if is_connected():
					if amt_left < 500 and amt_left > 0:
						mt = MessageTemplate.objects.get(m_type=2)
						if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
							text = mt.text.format(cons.flat.owner, cons.flat.flat, cons.flat.tower, round(amt_left))
							mt.SendSMS(text, cons.flat)
							sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
					elif amt_left < 0:
						mt = MessageTemplate.objects.get(m_type=3)
						if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
							text = mt.text.format(cons.flat.owner, cons.flat.tower, cons.flat.flat, round(amt_left))
							mt.SendSMS(text, cons.flat)
							sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
				Consumption.objects.filter(flat__id=cp.flat_id).update(amt_left=amt_left, ng_eb=ng_eb, ng_dg=ng_dg, eb=cp.eb, dg=cp.dg, deduction_status=2, status=status)
			elif cp.eb < cons.getLastEB() or cp.dg < cons.getLastDG():
				status = getConsumptionStatus(float(cons.amt_left))
				Consumption.objects.filter(flat__id=cp.flat_id).update(deduction_status = 1, status=status)
				# cons.save()
			elif cp.eb == cons.getLastEB() or cp.dg == cons.getLastDG():
				status = getConsumptionStatus(float(cons.amt_left))
				Consumption.objects.filter(flat__id=cp.flat_id).update(status = status)
				
		SentMessage.objects.bulk_create(sms)		
		#Consumption.objects.bulk_update(l, ['amt_left', 'ng_eb', 'ng_dg', 'eb', 'dg', 'last_deduction_dt'])

@periodic_task(run_every=crontab(minute='*/5'))
def WriteFlatStatus():
	c = Consumption.objects.filter(flat__status=1)
	cur.executemany("update TblConsumption set status=? where flat_pkey=?", [(i.status, i.flat_id) for i in c])
	conn.commit()



@periodic_task(run_every=crontab(hour="*", minute=0))
def LogReading():
	print("LogReading")
	c = Consumption.objects.filter(flat__status=1)
	readings = []
	for i in c:
		da = DeductionAmt.objects.get(tower=i.flat.tower)
		readings.append(Reading(flat=i.flat, eb=i.eb, dg=i.dg, eb_price=da.eb_price, dg_price=da.dg_price, amt_left=i.amt_left))

	Reading.objects.bulk_create(readings)


@periodic_task(run_every=crontab(minute=5, hour=0))
def MaintanceFixed():
	print("MaintanceFixed")
	c = list(Consumption.objects.filter(flat__id=731))
	maint = []
	for i in c:
		last = Maintance.objects.filter(flat=i.flat).order_by("-dt")[0].dt
		dt_now = timezone.localtime(timezone.now())
		consumed = 0
		while last <= dt_now:
			last_local = timezone.localtime(last)
			if not Maintance.objects.filter(flat=i.flat, dt__year=last_local.year, dt__month=last_local.month, dt__day=last_local.day).exists():
				maint.append(Maintance(flat=i.flat, mrate=i.flat.getMRate(), mcharge=i.flat.getMaintance(), famt=i.flat.getFixed(), dt=last.astimezone(pytz.utc)))
				i.amt_left = float(i.amt_left)-i.flat.getMFTotal()
			last = last+timedelta(days=1)
	Maintance.objects.bulk_create(maint)
	Consumption.objects.bulk_update(c, ['amt_left'])

def Billing():
	print("billing")
	create = []
	dt = timezone.now()
	next_dt = dt+timedelta(days=1)
	bills = MonthlyBill.objects.filter(month=dt.month, year=dt.year)
	for b in bills:
		reading = Reading.objects.filter(flat=b.flat).order_by("-dt")[0]
		da = DeductionAmt.objects.get(tower=b.flat.tower)
		MonthlyBill.objects.filter(id=b.id).update(end_eb=reading.eb, end_dg=reading.dg, cls_amt=b.flat.consumption.amt_left)
		create.append(MonthlyBill(flat=b.flat, month=next_dt.month, year=next_dt.year, start_eb=reading.eb, \
			start_dg=reading.dg, end_eb=0, end_dg=0, opn_amt=b.flat.consumption.amt_left, cls_amt=0, eb_price=float(da.eb_price), \
				dg_price=float(da.dg_price)))
	MonthlyBill.objects.bulk_create(create)


def RefMaintance():
	c = Consumption.objects.filter(flat__id=754).exclude(flat__tower=17)
	maint = []
	for i in c:
		print(i)
		last3 = Maintance.objects.filter(flat=i.flat).order_by("-dt")[:3]
		for m in last3:
			i.amt_left = float(i.amt_left)+(float(m.mcharge)-i.flat.getMaintance())
			m.mcharge = i.flat.getMaintance()
			m.mrate = 1.79
			maint.append(m)
		print(i.amt_left)
	Maintance.objects.bulk_update(maint, ['mcharge', 'mrate'])
	Consumption.objects.bulk_update(c, ['amt_left'])

def BackMaint():
	m = Maintance.objects.filter(dt__month=11, dt__year=2019, dt__day=12)