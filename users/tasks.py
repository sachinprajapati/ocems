from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import timedelta, date, datetime
from collections import namedtuple

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
		nc = Consumptions(*i)
		try:
			cos = Consumption.objects.get(id=nc.flat_id)
			cos.eb = i.eb
			cos.dg = i.dg
			if cos.deduction_status == "N":
				cos.deduction_status = 1
			elif cos.deduction_status == "Y":
				cos.deduction_status = 2
			cos.save()
		except Exception as e:
			print(e)