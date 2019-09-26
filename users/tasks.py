from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import timedelta, date, datetime
from collections import namedtuple
from django.db import transaction

from celery.task import periodic_task

from .models import *
from ocems.settings import conn

cur = conn.cursor()

@periodic_task(run_every=timedelta(seconds=30))
def ReadEbAndDG():
	Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption]")
	c = c.fetchall()
	l = []
	for i in c:
		cp = Consumptions(*i)
		flat = Flats.objects.get(id=cp.flat_id)
		cons = Consumption.objects.get(flat=flat)
		if cp.eb != cons.eb and cp.dg != ciel(cons.dg):
			print("flat is ", flat, round(cons.dg), cp.dg, " dg ", round(cons.dg)-cp.dg)
		# try:
		# 	with transaction.atomic():
		# 		da = DeductionAmt.objects.get(tower=flat.tower)
		# 		last_reading = Reading.objects.filter(flat=flat).order_by('-dt')[0]
		# 		eb_charge = (nc.eb-last_reading.eb)*da.eb_price
		# 		dg_charge = (nc.dg-last_reading.dg)*da.dg_price
		# 		amt_left = cons.amt_left-(eb_charge+dg_charge)
		# 		r = Reading(flat=flat, eb=nc.eb, dg=nc.dg, eb_price=da.eb_price, dg_price=da.dg_price, mrate=da.maintance, famt=da.fixed_amt, amt_left=amt_left)
		# 		r.save()
		# 		cons.eb = i.eb
		# 		cons.dg = i.dg
		# 		cons.amt_left= amt_left
		# 		if cons.deduction_status == "N":
		# 			cons.deduction_status = 1
		# 		elif cons.deduction_status == "Y":
		# 			cons.deduction_status = 2
		# 		cons.save()
		# except Exception as e:
		# 	print(e)


@periodic_task(run_every=timedelta(seconds=30))
def MaintanceAndFixed():
	pass