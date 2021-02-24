from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from ocems.settings import conn

import pytz
import socket
import calendar
import requests
from datetime import datetime

def dt_now():
	dt = timezone.now()
	utc = dt.replace(tzinfo=pytz.UTC)
	localtz = pytz.timezone("Asia/Calcutta")
	localtz = utc.astimezone(localtz)
	return localtz


FLAT_STATUS = (
    (1, _("Occupied")),
    (2, _("Vacant"))
)

BOOLEAN_BASIS = (
	(1, _("N")),
    (2, _("Y"))
)

FLAT_TYPE = [
	(1, 'Penthouse'),
	(2, '2BHK'),
	(3, '3BHK'),
]

class Flats(models.Model):
	tower = models.PositiveIntegerField()
	flat = models.PositiveIntegerField()
	owner = models.CharField(max_length=255, null=True, blank=True)
	flat_size = models.PositiveIntegerField()
	profession = models.CharField(max_length=255, null=True, blank=True)
	status = models.PositiveIntegerField(choices=FLAT_STATUS, default=1)
	phone_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{10}', message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.")
	phone = models.DecimalField(validators=[phone_regex], max_digits=10, decimal_places=0, null=True, blank=True)
	email = models.EmailField(max_length=255, null=True, blank=True)
	meter_sr = models.TextField(null=True, blank=True)
	basis = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	fixed_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	Type = models.PositiveIntegerField(choices=FLAT_TYPE, null=True)

	def __str__(self):
		return 'tower {} flat {} owner {}'.format(self.tower, self.flat, self.owner)

	def getMaintance(self):
		if self.tower == 17:
			return 0
		m = DeductionAmt.objects.get(tower=self.tower).maintance
		return (float(m)*self.flat_size)*(12/365)

	def getFixed(self):
		if self.tower == 17:
			return float(self.fixed_amt)*(12/365)
		m = DeductionAmt.objects.get(tower=self.tower).fixed_amt
		return float(m)*(12/365)

	def getMRate(self):
		if self.tower == 17:
			return 0
		return float(DeductionAmt.objects.get(tower=self.tower).maintance)

	def getMFTotal(self):
		return self.getMaintance()+self.getFixed()

	def get_absolute_url(self):
		return reverse('users:select_flat')

CONSUMPTION_STATUS = (
	(0, _("Enough Balance")),
    (1, _("Low Balance")),
	(2, _("Negative Balance")),
	(3, _("Power Cut"))
)


class Consumption(models.Model):
	dt = models.DateTimeField()
	flat = models.OneToOneField(Flats, on_delete=models.CASCADE)
	eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG KWH")
	start_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Start Utility KWH")
	start_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Start DG KWH")
	amt_left = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Amount Left")
	status = models.PositiveIntegerField(choices=CONSUMPTION_STATUS, null=True, blank=True)
	reset_dt = models.DateTimeField(null=True, blank=True)
	meter_change_dt = models.DateTimeField(null=True, blank=True)
	last_modified = models.CharField(max_length=5)
	last_deduction_dt = models.DateTimeField()
	deduction_status = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	ng_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Negative Utility KWH")
	ng_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Negative DG KWH")
	ng_dt = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return '{}/{} Amount {}'.format(self.flat.tower, self.flat.flat, self.amt_left)


	def getLastEB(self):
		return float(self.ng_eb)+float(self.start_eb)

	def getLastDG(self):
		return float(self.ng_dg)+float(self.start_dg)


RECHARGE_TYPE = (
	(1, _("cash")),
    (2, _("bank")),
	(3, _("neft")),
	(4, _("merchant"))
)

class Recharge(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	amt_left = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Amount Left")
	recharge = models.PositiveIntegerField()
	Type = models.PositiveIntegerField(choices=RECHARGE_TYPE, null=True, blank=True)
	chq_dd = models.CharField(max_length=255, null=True, blank=True)
	eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG KWH")
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} recharge {}'.format(self.flat, self.recharge)

	# def save(self, *args, **kwargs):
	#     super(Recharge, self).save(*args, **kwargs)

@receiver(post_save, sender=Recharge, dispatch_uid="update_stock_count")
def update_stock(sender, instance, created, **kwargs):
	if created and instance.flat.phone:
		mt = MessageTemplate.objects.get(m_type=1)
		text = mt.text.format(instance.flat.owner, instance.flat.tower, instance.flat.flat, instance.recharge, instance.flat.consumption.amt_left)
		mt.sendMessage(text, instance.flat)
		print("sending message to ", instance.flat)
	else:
		print("cannot send message to ", instance)


def get_days(start_dt, end_dt, month, year):
	tmp_end_dt = datetime(year, month, calendar.monthrange(year, month)[1]).date()
	tmp_start_dt = datetime(year, month, 1).date()
	if not end_dt:
		end_dt = tmp_end_dt
	elif end_dt > tmp_end_dt:
		end_dt = tmp_end_dt
	if start_dt < tmp_start_dt:
		start_dt = tmp_start_dt
	print("days is", end_dt.day-start_dt.day+1)
	return end_dt.day-start_dt.day+1


class MonthlyBill(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	month = models.PositiveIntegerField()
	year = models.PositiveIntegerField()
	start_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Start Utility KWH")
	start_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Start DG KWH")
	end_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="End Utility KWH")
	end_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="End DG KWH")
	opn_amt = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Opening Amount")
	cls_amt = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Closing Amount")
	eb_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility Rate")
	dg_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG Rate")
	start_dt = models.DateTimeField(auto_now_add=True)
	end_dt = models.DateTimeField(null=True, blank=True, auto_now=True)

	def __str__(self):
		return '{} month {} year {}'.format(self.flat, self.month, self.year)

	def get_eb(self):
		return self.end_eb-self.start_eb

	def get_ebprice(self):
		return float(float(self.eb_price)*float(self.get_eb()))

	def get_dg(self):
		return self.end_dg-self.start_dg

	def get_dgprice(self):
		return float(self.dg_price)*float(self.get_dg())

	def get_OtherMaintance(self):
		if self.flat.tower==17:
			return None
		# if self.month<=11 and self.year==2019:
		# 	return OtherMaintance.objects.filter(start_dt__month=self.month, start_dt__year=self.year)
		# else:
		end_dt = datetime(self.year, self.month, calendar.monthrange(self.year, self.month)[1]).date()
		om = OtherMaintance.objects.filter(start_dt__lte=end_dt)
		# om = OtherMaintance.objects.filter(start_dt__year__lte=self.year)
		l = []
		for i in om:
			if i.end_dt:
				if i.end_dt >= datetime(self.year, self.month, 1).date():
					l.append(i)
			elif i.start_dt.month == self.month:
				l.append(i)
		return l

	def get_OtherMaintanceTotal(self):
		if self.flat.tower == 17:
			return 0
		total = 0
		om = self.get_OtherMaintance()
		for i in om:
			days = get_days(i.start_dt, i.end_dt, self.month, self.year)
			total += ((self.flat.flat_size*i.price)*(12/365))*days
		return total

	def get_TotalMaintance(self):
		m = Maintance.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Coalesce(Sum('mcharge'), 0))
		print("m is",m['mcharge__sum'])
		return float(m['mcharge__sum'] if m['mcharge__sum'] else 0)-self.get_OtherMaintanceTotal()

	def get_TotalFixed(self):
		f = Maintance.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('famt')) or 0
		return float(f['famt__sum'])

	def Debits(self):
		return Debit.objects.filter(dt__month=self.month, dt__year=self.year, flat=self.flat)

	def TotalDebits(self):
		deits = self.Debits().aggregate(Sum('debit_amt'))['debit_amt__sum'] or 0
		return deits+self.get_OtherMaintanceTotal()

	def get_TotalUsed(self):
		t = self.get_ebprice()+self.get_dgprice()+self.get_TotalMaintance()+self.get_TotalFixed()+self.TotalDebits()
		return float(t)

	def get_RechargeInMonth(self):
		r = Recharge.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('recharge')) or 0
		return float(r['recharge__sum'])

	def get_Adjustment(self):
		return float(self.opn_amt)+self.get_RechargeInMonth()-self.get_TotalUsed()-float(self.cls_amt)

class Maintance(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	dt = models.DateTimeField()
	mrate = models.DecimalField(max_digits=19, decimal_places=4,verbose_name=_("Maintance Rate"))
	mcharge = models.DecimalField(max_digits=19, decimal_places=4,verbose_name=_("Maintance Charges"))
	famt = models.DecimalField(max_digits=19, decimal_places=4,verbose_name=_("Fixed Amount"))

	def __str__(self):
		return '{}'.format(self.flat)


class Reading(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG KWH")
	eb_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility Rate")
	dg_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG Rate")
	amt_left = models.DecimalField(max_digits=19, decimal_places=4)
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} {}'.format(self.flat, self.amt_left)


class DeductionAmt(models.Model):
	tower = models.PositiveIntegerField(unique=True)
	tower_name = models.CharField(max_length=10)
	eb_price = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="Utility Rate")
	dg_price = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="DG Rate")
	maintance = models.DecimalField(max_digits=19, decimal_places=2)
	fixed_amt = models.DecimalField(max_digits=19, decimal_places=2)
	set_load = models.FloatField(null=True)

	def __str__(self):
		return '{} eb {} dg {} maintance {} fixed {}'.format(self.tower, self.eb_price, self.dg_price, self.maintance, self.fixed_amt)

	def get_update_url(self):
		return reverse('users:tower_update', kwargs={'pk': self.pk})

	def save(self, *args, **kwargs):
		cur = conn.cursor()
		cur.execute("update [EMS].[dbo].[TblConsumption] set max_load=? where Tower_No=?", [self.set_load, self.tower])
		conn.commit()
		super().save(*args, **kwargs)



class MeterChange(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	amt_left = models.DecimalField(max_digits=19, decimal_places=4)
	old_meter_sr = models.TextField(null=True, blank=True, verbose_name="Old Meter Serial Number")
	old_start_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Start Utility KWH")
	old_ng_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Consumed Utility KWH")
	old_last_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Last Utility KWH")
	old_start_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Start DG KWH")
	old_ng_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Consumed DG KWH")
	old_last_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Old Last DG KWH")
	new_meter_sr = models.TextField(null=True, blank=True, verbose_name="New Meter Serial Number")
	new_start_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="New Start Utility KWH")
	new_start_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="New Start DG KWH")
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} {}'.format(self.flat, self.amt_left)

	
FEEDER_TYPE = (
	(1, _("Incoming")),
    (2, _("Outgoing")),
)

PS_TYPE = (
	(1, _("PS2")),
    (2, _("PS1")),
)

class Feeder(models.Model):
	ps_key = models.PositiveIntegerField(choices=PS_TYPE)
	name = models.CharField(max_length=255)
	desc = models.TextField(null=True)
	eb = models.DecimalField(max_digits=19, decimal_places=4, null=True, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, null=True, verbose_name="DG KWH")
	load = models.DecimalField(max_digits=19, decimal_places=4, null=True, verbose_name="Running Load")
	f_type = models.PositiveIntegerField(choices=FEEDER_TYPE, null=True, blank=True)

class FeederReadings(models.Model):
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)
	feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE)
	eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG KWH")
	load = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Running Load")


Message_TYPE = (
	(1, _("Recharge")),
    (2, _("Low Balance")),
    (3, _("Negative Balance")),
    (4, _("Compose")),
)


def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

class MessageTemplate(models.Model):
	m_type = models.PositiveIntegerField(choices=Message_TYPE, unique=True)
	text = models.TextField()

	def __str__(self):
		return '{} - {}'.format(self.get_m_type_display(), self.text)

	def sendMessage(self, text, flat):
		if is_connected():
			self.SendSMS(text, flat)
		else:
			pass
			# print("internet is not working")

	def SendSMS(self, text, flat):
		URL = "https://www.txtguru.in/imobile/api.php"
		# PARAMS = {'username': 'orangecounty.csk',
        #   'password': '86617614',
        #   'source': 'OCAOAM',
        #   'dmobile': '91{}'.format(flat.phone),
        #   'message': text}
		# r = requests.get(url = URL, params = PARAMS, timeout=2)
		# if r.status_code == 200:
		# 	sm = SentMessage(flat=flat, m_type=self, text=text)
		# 	sm.save()


class SentMessage(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	m_type = models.ForeignKey(MessageTemplate, on_delete=models.SET_NULL, null=True)
	text = models.TextField()
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return 'tower {} flat {} type {} at {}'.format(self.flat.tower, self.flat.flat, self.m_type.get_m_type_display(), self.dt.strftime("%d/%m/%y %H:%M %p"))

class Debit(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	amt_left = models.DecimalField(max_digits=19, decimal_places=4)
	debit_amt = models.PositiveIntegerField()
	eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility KWH")
	dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG KWH")
	remarks = models.TextField(null=True)
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} debit amt {} at {}'.format(self.flat, self.amt_left, self.dt)

CHARGE_FLAT_TYPE = [
	
]

class OtherMaintance(models.Model):
	price = models.PositiveIntegerField()
	name = models.CharField(max_length=255)
	start_dt = models.DateField()
	end_dt = models.DateField(null=True, blank=True)
	tower = models.ManyToManyField(DeductionAmt)

	def __str__(self):
		return 'from {} to {} of {} price {}'.format(self.start_dt, self.end_dt, self.name, self.price)

class PowerCut(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	running_load = models.FloatField()
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} at {}'.format(self.flat, self.dt)
