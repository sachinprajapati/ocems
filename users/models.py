from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum
import pytz

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
		return '{} {} {}'.format(self.tower, self.flat, self.owner)


class Consumption(models.Model):
	datetime = models.DateTimeField()
	flat = models.OneToOneField(Flats, on_delete=models.CASCADE)
	eb = models.FloatField(default=0, verbose_name="Utility KWH")
	dg = models.FloatField(default=0, verbose_name="DG KWH")
	ref_eb = models.FloatField(default=0, verbose_name="Ref Utility KWH")
	ref_dg = models.FloatField(default=0, verbose_name="Ref DG KWH")
	start_eb = models.FloatField(default=0, verbose_name="Start Utility KWH")
	start_dg = models.FloatField(default=0, verbose_name="Start DG KWH")
	amt_left = models.FloatField(default=0, verbose_name="Amount Left")
	status = models.PositiveIntegerField(null=True, blank=True)
	reset_dt = models.DateTimeField(null=True, blank=True)
	meter_change_dt = models.DateTimeField(null=True, blank=True)
	last_modified = models.CharField(max_length=5)
	last_deduction_dt = models.DateTimeField()
	deduction_status = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	ng_eb = models.FloatField(default=0, verbose_name="Negative Utility KWH")
	ng_dg = models.FloatField(default=0, verbose_name="Negative DG KWH")
	ng_dt = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return '{} amt left {} eb {} and dg {}'.format(self.flat.owner, self.amt_left, self.eb, self.dg)


RECHARGE_TYPE = (
	(1, _("cash")),
    (2, _("bank"))
)

class Recharge(models.Model):
	sno = models.PositiveIntegerField(null=True, blank=True)
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	amt_left = models.FloatField(default=0, verbose_name="Amount Left")
	recharge = models.PositiveIntegerField()
	Type = models.PositiveIntegerField(choices=RECHARGE_TYPE, null=True, blank=True)
	chq_dd = models.PositiveIntegerField(null=True, blank=True)
	eb = models.FloatField(default=0, verbose_name="Utility KWH")
	dg = models.FloatField(default=0, verbose_name="DG KWH")
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return '{} recharge {}'.format(self.flat, self.recharge)

class MonthlyBill(models.Model):
	Bill_Pkey = models.PositiveIntegerField()
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	month = models.PositiveIntegerField()
	year = models.PositiveIntegerField()
	start_eb = models.FloatField(default=0, verbose_name="Start Utility KWH")
	start_dg = models.FloatField(default=0, verbose_name="Start DG KWH")
	end_eb = models.FloatField(default=0, verbose_name="End Utility KWH")
	end_dg = models.FloatField(default=0, verbose_name="End DG KWH")
	opn_amt = models.FloatField(default=0, verbose_name="Opening Amount")
	cls_amt = models.FloatField(default=0, verbose_name="Closing Amount")
	eb_price = models.FloatField(default=0, verbose_name="Utility Rate")
	dg_price = models.FloatField(default=0, verbose_name="DG Rate")
	start_dt = models.DateTimeField()
	end_dt = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return '{} month {} year {}'.format(self.flat, self.month, self.year)

	def get_eb(self):
		return self.end_eb-self.start_eb

	def get_ebprice(self):
		return self.eb_price*self.get_eb()

	def get_dg(self):
		return self.end_dg-self.start_dg

	def get_dgprice(self):
		return self.dg_price*self.get_dg()

	def get_TotalMaintance(self):
		m = Maintance.objects.filter(flat=self.flat, Date__month=self.month, Date__year=self.year).aggregate(Sum('mcharge'))
		return m['mcharge__sum']

	def get_TotalFixed(self):
		f = Maintance.objects.filter(flat=self.flat, Date__month=self.month, Date__year=self.year).aggregate(Sum('famt'))
		return f['famt__sum']

	def get_TotalUsed(self):
		t = self.get_ebprice()+self.get_dgprice()+self.get_TotalMaintance()+self.get_TotalFixed()
		return t

	def get_RechargeInMonth(self):
		r = Recharge.objects.filter(flat=self.flat, dt__month=self.month, dt__year=self.year).aggregate(Sum('recharge'))
		return r['recharge__sum']

class Maintance(models.Model):
	sno = models.PositiveIntegerField()
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	Date = models.DateTimeField()
	mrate = models.FloatField(verbose_name=_("Maintance Rate"))
	flat_size = models.PositiveIntegerField()
	mcharge = models.FloatField(verbose_name=_("Maintance Charges"))
	famt = models.FloatField(verbose_name=_("Fixed Amount"))
	field_amt = models.FloatField()

	def __str__(self):
		return '{}'.format(self.flat)


class Reading(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	eb = models.FloatField(default=0, verbose_name="Utility KWH")
	dg = models.FloatField(default=0, verbose_name="DG KWH")
	ref_eb = models.FloatField(default=0, verbose_name="Ref Utility KWH")
	ref_dg = models.FloatField(default=0, verbose_name="Ref DG KWH")
	eb_price = models.FloatField(default=0, verbose_name="Utility Rate")
	dg_price = models.FloatField(default=0, verbose_name="DG Rate")
	mrate = models.FloatField(verbose_name=_("Maintance Rate"))
	famt = models.FloatField(verbose_name=_("Fixed Amount"))
	amt_left = models.FloatField()
	dt = models.DateTimeField(auto_now_add=False, auto_now=True)

	def __str__(self):
		return '{} {}'.format(self.flat, self.amt_left)


class DeductionAmt(models.Model):
	tower = models.PositiveIntegerField()
	tower_name = models.CharField(max_length=10)
	eb_price = models.FloatField(verbose_name="Utility Rate")
	dg_price = models.FloatField(verbose_name="DG Rate")
	maintance = models.FloatField()
	fixed_amt = models.FloatField()

	def __str__(self):
		return '{} eb {} dg {} maintance {} fixed {}'.format(self.tower, self.eb_price, self.dg_price, self.maintance, self.fixed_amt)