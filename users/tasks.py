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

import socket

#cur = conn.cursor()

def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data

def getTCPData():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.1.5', 5000))
    response = recvall(client)
    return json.loads(response.decode('utf-8'))

@periodic_task(run_every=crontab(minute="*"))
def ReadEbAndDG():
	print("ReadEbAndDG")
	# Consumptions = namedtuple("Consumptions", ['flat_id', 'eb', 'dg'])
	# c = cur.execute("SELECT flat_pkey, Utility_KWH as eb, DG_KWH as dg FROM [EMS].[dbo].[TblConsumption]")
	# c = c.fetchall()
	# l = []
	# for i in c:
	# 	cp = Consumptions(*i)
	# 	cons = Consumption.objects.get(flat__id=cp.flat_id)
	# 	da = DeductionAmt.objects.get(tower=cons.flat.tower)
	# 	if cp.eb > float(cons.eb) or cp.dg > float(cons.dg):
	# 		consumed = ((cp.eb-float(cons.ng_eb))*float(da.eb_price))+((cp.dg-float(cons.ng_dg))*float(da.dg_price))
	# 		cons.amt_left = float(cons.amt_left)-consumed
	# 		cons.ng_eb = cons.eb
	# 		cons.ng_dg = cons.dg
	# 		cons.eb = i.eb
	# 		cons.dg = i.dg
	# 		cons.last_deduction_dt = timezone.now()
	# 		l.append(cons)
	# Consumption.objects.bulk_update(l, ['amt_left', 'ng_eb', 'ng_dg', 'eb', 'dg', 'last_deduction_dt'])


@periodic_task(run_every=crontab(hour="*", minute=0))
def LogReading():
	print("LogReading")
	# c = Consumption.objects.all()
	# readings = []
	# for i in c:
	# 	da = DeductionAmt.objects.get(tower=i.flat.tower)
	# 	readings.append(Reading(flat=i.flat, eb=i.eb, dg=i.dg, eb_price=da.eb_price, dg_price=da.dg_price, amt_left=i.amt_left))

	# Reading.objects.bulk_create(readings)


@periodic_task(run_every=crontab(minute=0, hour=0))
def MaintanceFixed():
	print("MaintanceFixed")
	# c = list(Consumption.objects.all())
	# maint = []
	# for i in c:
	# 	maint.append(Maintance(flat=i.flat, mrate=i.flat.getMRate(), mcharge=i.flat.getMaintance(),famt=i.flat.getFixed(),field_amt=0))
	# 	i.amt_left = float(i.amt_left)-i.flat.getMFTotal()

	# Maintance.objects.bulk_create(maint)
	# Consumption.objects.bulk_update(c, ['amt_left'])


@periodic_task(run_every=crontab(minute=53, hour=0))
def TestingTask():
	print("TestingTask ",timezone.now())
