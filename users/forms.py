from django.forms import ModelForm
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import *


class RechargeForm(ModelForm):
	class Meta:
		model = Recharge
		fields = ['flat', 'recharge', 'Type', 'chq_dd']


	def save(self, commit=True):
		m = super(RechargeForm, self).save(commit=False)
		try:
			with transaction.atomic():
				obj = Consumption.objects.get(flat=m.flat)
				m.amt_left = obj.amt_left
				obj.amt_left += m.recharge
				m.eb = obj.eb
				m.dg = obj.dg
				if obj.deduction_status == "Y":
					obj.deduction_status = 2
				elif obj.deduction_status == "N":
					obj.deduction_status = 1
				obj.save()
				m.save()
				return m
		except Exception as e:
			print(e)
			return False