from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import *

COMPLAINT_STATUS = (
	(1, _("Active")),
    (2, _("In progress")),
	(3, _("Closed"))
)

class Complaint(models.Model):
	flat = models.ForeignKey(Flats, on_delete=models.CASCADE)
	phone_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{10}', message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed.")
	phone = models.DecimalField(validators=[phone_regex], max_digits=10, decimal_places=0, null=True, blank=True)
	remark = models.TextField(verbose_name='Remark')
	status = models.PositiveSmallIntegerField(choices=COMPLAINT_STATUS, default=1)
	dt = models.DateTimeField(auto_now_add=True, auto_now=False)
	solved_dt = models.DateTimeField(blank=True, null=True)

NOTICE_STATUS = (
	(1, _("Active")),
	(2, _("Inactive"))
)

class Notice(models.Model):
	sub = models.CharField(max_length=255, verbose_name="Subject")
	text = models.TextField()
	status = models.PositiveSmallIntegerField(choices=NOTICE_STATUS, default=1)
	dt = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '{}'.format(self.sub)
