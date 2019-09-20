from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

FLAT_STATUS = (
    (1, _("Occupied")),
    (2, _("Vacant"))
)

FLAT_BASIS = (
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
	basis = models.PositiveIntegerField(choices=FLAT_BASIS, null=True, blank=True)
	fixed_amt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	def __str__(self):
		return '{} {} {}'.format(self.tower, self.flat, self.owner)