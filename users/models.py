from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

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
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	no = models.PositiveIntegerField()
	amt_left = models.FloatField(default=0, verbose_name="Amount Left")
	recharge = models.PositiveIntegerField()
	Type = models.PositiveIntegerField(choices=BOOLEAN_BASIS, null=True, blank=True)
	chq_dd = models.PositiveIntegerField(null=True, blank=True)
	eb = models.FloatField(default=0, verbose_name="Utility KWH")
	dg = models.FloatField(default=0, verbose_name="DG KWH")
	dt = models.DateTimeField()
