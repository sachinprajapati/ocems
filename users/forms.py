from django.forms import ModelForm
from django import forms
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


class SendSMS(forms.Form):
	id = forms.IntegerField()
	message = forms.CharField(widget=forms.Textarea())

	def clean_id(self):
		try:
			flat = Flats.objects.get(id=self.cleaned_data['id'])
		except Exception as e:
			raise ValidationError(e)
		return flat

	def send_email(self):
		print("message sent")


class MeterChangeForm(forms.Form):
	id = forms.IntegerField()
	New_EB = forms.IntegerField()
	New_Dg = forms.IntegerField()
	Meter_Serial_Number = forms.CharField(required=False)

	def clean_id(self):
		try:
			flat = Flats.objects.get(id=self.cleaned_data['id'])
		except Exception as e:
			raise ValidationError(e)
		return flat