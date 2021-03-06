from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.task.schedules import crontab
from datetime import timedelta, date, datetime
from django.utils import timezone
from collections import namedtuple
from django.db import transaction
from django.db.models import Avg, Case, Count, F, Max, Min

from celery.task import periodic_task

from .models import *
from ocems.settings import conn

import urllib.request
import json
import pytz
import time

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

@periodic_task(run_every=crontab(minute='*/30'))
def ReadEbAndDG():
	print("ReadEbAndDG")
	Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	cur = conn.cursor()
	c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption] where flat_pkey!=916")
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
				# if is_connected() and dtnow.hour >= 7:
				# 	if amt_left < 500 and amt_left > 0 and cons.flat.phone:
				# 		mt = MessageTemplate.objects.get(m_type=2)
				# 		if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
				# 			text = mt.text.format(cons.flat.owner, cons.flat.flat, cons.flat.tower, round(amt_left))
				# 			mt.SendSMS(text, cons.flat)
				# 			sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
				# 	elif amt_left < 0 and cons.flat.phone and amt_left >= -1000:
				# 		mt = MessageTemplate.objects.get(m_type=3)
				# 		if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
				# 			text = mt.text.format(cons.flat.owner, cons.flat.tower, cons.flat.flat, round(amt_left))
				# 			mt.SendSMS(text, cons.flat)
				# 			sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
				try:
					Consumption.objects.filter(flat__id=cp.flat_id).update(amt_left=amt_left, ng_eb=ng_eb, ng_dg=ng_dg, \
					eb=float(cp.eb), dg=float(cp.dg), deduction_status=2, status=status, last_deduction_dt=timezone.now())
				except Exception as e:
					print(e, "with cp", cp)
			elif cp.eb < cons.getLastEB() or cp.dg < cons.getLastDG():
				status = getConsumptionStatus(float(cons.amt_left))
				Consumption.objects.filter(flat__id=cp.flat_id).update(deduction_status = 1, status=status)
				# cons.save()
			elif cp.eb == cons.getLastEB() or cp.dg == cons.getLastDG():
				status = getConsumptionStatus(float(cons.amt_left))
				Consumption.objects.filter(flat__id=cp.flat_id).update(status = status)
		SentMessage.objects.bulk_create(sms)
		#Consumption.objects.bulk_update(l, ['amt_left', 'ng_eb', 'ng_dg', 'eb', 'dg', 'last_deduction_dt'])

@periodic_task(run_every=crontab(minute='*/10', hour="10-19"))
def WriteFlatStatus():
	cur = conn.cursor()
	#c = Consumption.objects.filter(flat__status=1)
	cur.executemany("update TblConsumption set status=? where flat_pkey=?", Consumption.objects.filter(flat__status=1).values_list('status', 'flat_id').iterator())
	conn.commit()



@periodic_task(run_every=crontab(hour="*/2", minute=0))
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
	c = list(Consumption.objects.filter(flat__status=1))
	maint = []
	for i in c:
		maint.append(Maintance(flat=i.flat, mrate=i.flat.getMRate(), mcharge=i.flat.getMaintance(),famt=i.flat.getFixed(), dt=timezone.now()))
		i.amt_left = float(i.amt_left)-i.flat.getMFTotal()

	Maintance.objects.bulk_create(maint)
	Consumption.objects.bulk_update(c, ['amt_left'])

def Billing():
	print("billing")
	create = []
	dt = timezone.now()
	next_dt = dt+timedelta(days=1)
	bills = MonthlyBill.objects.filter(month=4, year=2021, flat__status=1)
	# bills = MonthlyBill.objects.filter(month=2, year=2020, flat__status=1)
	objs = []
	r = Reading.objects.filter(dt__day=1, dt__month=5, dt__year=2021).values('flat_id').annotate(Max('amt_left'), Min('eb'), Min('dg'))
	for b in bills:
		# reading = Reading.objects.filter(flat=b.flat, dt__day=dt.day, dt__month=dt.month, dt__year=dt.year).order_by("-dt")[0]
		#reading = Reading.objects.filter(flat=b.flat, dt__day=1, dt__month=5, dt__year=2021).order_by("dt")[0]
		da = DeductionAmt.objects.get(tower=b.flat.tower)
		# MonthlyBill.objects.filter(id=b.id).update(end_eb=reading.eb, end_dg=reading.dg, cls_amt=reading.amt_left)
		reading = r.get(flat_id=b.flat_id)
		b.end_eb = reading['eb__min']
		b.end_dg = reading['dg__min']
		b.cls_amt = reading['amt_left__max']
		objs.append(b)
		create.append(MonthlyBill(flat=b.flat, month=5, year=2021, start_eb=reading['eb__min'], \
			start_dg=reading['dg__min'], end_eb=0, end_dg=0, opn_amt=reading['amt_left__max'], cls_amt=0, eb_price=float(da.eb_price), \
				dg_price=float(da.dg_price)))
	MonthlyBill.objects.bulk_update(objs, ['end_eb', 'end_dg', 'cls_amt'])
	MonthlyBill.objects.bulk_create(create)

@periodic_task(run_every=crontab(minute='*/5'))
def CheckLoad():
	cur = conn.cursor()
	dgsql = "SELECT dgstatus FROM TblDgStatus WHERE id=1"
	dgsql = cur.execute(dgsql)
	dgstatus = dgsql.fetchone()
	if dgstatus[0]:
		print("dg is on")
		sql = "SELECT flat_pkey, cur_load, status FROM [EMS].[dbo].[TblConsumption] where cur_load>max_load"
	else:
		print('Eb is on')
		sql = "SELECT flat_pkey, cur_load, status FROM [EMS].[dbo].[TblConsumption] where cur_load>max_load+2"
	c = cur.execute(sql)
	c = c.fetchall()
	pc = []
	if c:
		pc = [PowerCut(flat_id=i[0], running_load=i[1]) for i in c]
		cur.executemany("update [EMS].[dbo].[TblConsumption] set status=3 where flat_pkey=?", [[i[0]] for i in c])
		conn.commit()
		PowerCut.objects.bulk_create(pc)
		time.sleep(60*2)
		cur.executemany("update [EMS].[dbo].[TblConsumption] set status=? where flat_pkey=?", [[i[2], i[0]] for i in c])
		conn.commit()
	else:
		print("nothing")

