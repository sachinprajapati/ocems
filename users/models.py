from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum
import pytz
import socket

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
	status = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	reset_dt = models.DateTimeField(null=True, blank=True)
	meter_change_dt = models.DateTimeField(null=True, blank=True)
	last_modified = models.CharField(max_length=5)
	last_deduction_dt = models.DateTimeField()
	deduction_status = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	ng_eb = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Negative Utility KWH")
	ng_dg = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Negative DG KWH")
	ng_dt = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return '{} amt left {} eb {} and dg {}'.format(self.flat.owner, self.amt_left, self.eb, self.dg)


	def getLastEB(self):
		return float(self.ng_eb)+float(self.start_eb)

	def getLastDG(self):
		return float(self.ng_dg)+float(self.start_dg)


RECHARGE_TYPE = (
	(1, _("cash")),
    (2, _("bank")),
	(3, _("neft"))
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

	def save(self, *args, **kwargs):
	    mt = MessageTemplate.objects.get(m_type=1)
	    text = mt.text.format(self.flat.owner, self.flat.tower, self.flat.flat, self.recharge, self.amt_left+self.recharge)
	    mt.sendMessage(text, self.flat)
	    super(Recharge, self).save(*args, **kwargs)

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
	start_dt = models.DateTimeField()
	end_dt = models.DateTimeField(null=True, blank=True)

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

	def get_TotalMaintance(self):
		m = Maintance.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('mcharge'))
		if not m['mcharge__sum']:
			m['mcharge__sum'] = 0
		return float(m['mcharge__sum'])

	def get_TotalFixed(self):
		f = Maintance.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('famt'))
		if not f['famt__sum']:
			f['famt__sum'] = 0
		return float(f['famt__sum'])

	def Debits(self):
		return Debit.objects.filter(dt__month=self.month, dt__year=self.year, flat=self.flat)

	def TotalDebits(self):
		return self.Debits().aggregate(Sum('debit_amt'))['debit_amt__sum']

	def get_TotalUsed(self):
		t = self.get_ebprice()+self.get_dgprice()+self.get_TotalMaintance()+self.get_TotalFixed()+self.TotalDebits()
		return float(t)

	def get_RechargeInMonth(self):
		r = Recharge.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('recharge'))
		if not r['recharge__sum']:
			r['recharge__sum'] = 0
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
	eb_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="Utility Rate")
	dg_price = models.DecimalField(max_digits=19, decimal_places=4, verbose_name="DG Rate")
	maintance = models.DecimalField(max_digits=19, decimal_places=4)
	fixed_amt = models.DecimalField(max_digits=19, decimal_places=4)

	def __str__(self):
		return '{} eb {} dg {} maintance {} fixed {}'.format(self.tower, self.eb_price, self.dg_price, self.maintance, self.fixed_amt)



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
			sm = SentMessage(flat=flat, m_type=self, text=text)
			sm.save()
		else:
			pass
			# print("internet is not working")

	def SendSMS(self, text, flat):
		pass
		#print("sending message to ", flat, "mesage is -", text)


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
