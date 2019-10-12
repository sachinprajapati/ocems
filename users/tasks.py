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

cur = conn.cursor()

def getFlatData():
	try:
		response = urllib.request.urlopen('http://192.168.1.5:5000/hello/h', timeout=4)
		html = response.read()
		return json.loads(html)
	except Exception as e:
		print(e)
		return False
		


@periodic_task(run_every=crontab(minute='*/5'))
def ReadEbAndDG():
	print("ReadEbAndDG")
	Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	#c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption] where flat_pkey=728")
	#c = c.fetchall()
	c = getFlatData()
	if c:
		l = []
		sms = []
		for i in c["data"]:
			cp = Consumptions(**i)
			cons = Consumption.objects.get(flat__id=cp.flat_id)
			da = DeductionAmt.objects.get(tower=cons.flat.tower)
			if cp.eb > cons.getLastEB() or cp.dg > cons.getLastDG():
				consumed = (cp.eb-cons.getLastEB())*float(da.eb_price)+(cp.dg-cons.getLastDG())*float(da.dg_price)
				amt_left = float(cons.amt_left)-consumed
				ng_eb = cp.eb-float(cons.start_eb)
				ng_dg = cp.dg-float(cons.start_dg)
				eb = cp.eb
				dg = cp.dg
				dtnow = timezone.now()
				if is_connected():
					if amt_left < 500 and amt_left > 0:
						mt = MessageTemplate.objects.get(m_type=2)
						if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
							text = mt.text.format(cons.flat.owner, cons.flat.flat, cons.flat.tower, amt_left)
							mt.SendSMS(text, cons.flat)
							sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
					elif amt_left < 0:
						mt = MessageTemplate.objects.get(m_type=3)
						if not SentMessage.objects.filter(flat=cons.flat, dt__year=dtnow.year, dt__month=dtnow.month, dt__day=dtnow.day, m_type=mt).exists():
							text = mt.text.format(cons.flat.owner, cons.flat.tower, cons.flat.flat, amt_left)
							mt.SendSMS(text, cons.flat)
							sms.append(SentMessage(flat=cons.flat, m_type=mt, text=text))
					SentMessage.objects.bulk_create(sms)
				Consumption.objects.filter(flat__id=cp.flat_id).update(amt_left=amt_left, ng_eb=ng_eb, ng_dg=ng_dg, eb=cp.eb, dg=cp.dg, deduction_status=2)
			elif cp.eb < cons.getLastEB() or cp.dg < cons.getLastDG():
				Consumption.objects.filter(flat__id=cp.flat_id).update(deduction_status = 1)
				# cons.save()
		#Consumption.objects.bulk_update(l, ['amt_left', 'ng_eb', 'ng_dg', 'eb', 'dg', 'last_deduction_dt'])


@periodic_task(run_every=crontab(hour="*", minute=0))
def LogReading():
	print("LogReading")
	c = Consumption.objects.all()
	readings = []
	for i in c:
		da = DeductionAmt.objects.get(tower=i.flat.tower)
		readings.append(Reading(flat=i.flat, eb=i.eb, dg=i.dg, eb_price=da.eb_price, dg_price=da.dg_price, amt_left=i.amt_left))

	Reading.objects.bulk_create(readings)


@periodic_task(run_every=crontab(minute=0, hour=0))
def MaintanceFixed():
	print("MaintanceFixed")
	c = list(Consumption.objects.all())
	maint = []
	for i in c:
		maint.append(Maintance(flat=i.flat, mrate=i.flat.getMRate(), mcharge=i.flat.getMaintance(), famt=i.flat.getFixed()))
		i.amt_left = float(i.amt_left)-i.flat.getMFTotal()

	Maintance.objects.bulk_create(maint)
	Consumption.objects.bulk_update(c, ['amt_left'])