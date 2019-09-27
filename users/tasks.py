from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.task.schedules import crontab
from datetime import timedelta, date, datetime
from collections import namedtuple
from django.db import transaction

from celery.task import periodic_task

from .models import *
#from ocems.settings import conn

#cur = conn.cursor()

@periodic_task(run_every=timedelta(seconds=30))
def ReadEbAndDG():
	Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	#c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption]")
	#c = c.fetchall()
	c = [(728, 	108170.10, 	8517.8020)]
	l = []
	for i in c:
		cp = Consumptions(*i)
		flat = Flats.objects.get(id=cp.flat_id)
		cons = Consumption.objects.get(flat=flat)
		if cp.eb != cons.eb and cp.dg != cons.dg:
			print("flat is ", flat, cons.dg, cp.dg, " dg ")


@periodic_task(run_every=timedelta(minutes=0))
def LogReading():
	c = Consumption.objects.all()
	readings = []
	for i in c:
		da = DeductionAmt.objects.get(tower=i.flat.tower)
		readings.append(Reading(flat=i.flat, eb=i.eb, dg=i.dg, eb_price=da.eb_price, dg_price=da.dg_price, amt_left=i.amt_left))

	Reading.objects.bulk_create(readings)


@periodic_task(run_every=crontab(minute=0, hour=0))
def MaintanceFixed():
	c = list(Consumption.objects.all())
	maint = []
	for i in c:
		maint.append(Maintance(flat=i.flat, mrate=i.flat.getMRate(), mcharge=i.flat.getMaintance(),famt=i.flat.getFixed(),field_amt=0))
		i.amt_left = float(i.amt_left)-i.flat.getMFTotal()

	Maintance.objects.bulk_create(maint)
	Consumption.objects.bulk_update(c, ['amt_left'])