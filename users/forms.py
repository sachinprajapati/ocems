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
	flat_id = forms.IntegerField()
	message = forms.CharField(widget=forms.Textarea())

	def clean_flat_id(self):
		try:
			flat = Flats.objects.get(id=self.cleaned_data['flat_id'])
		except Exception as e:
			raise ValidationError(e)
		return flat

	def send_email(self):
		print("message sent")


class MeterChangeForm(ModelForm):
	# flat_id = forms.IntegerField()
	# New_EB = forms.IntegerField()
	# New_Dg = forms.IntegerField()
	# Meter_Serial_Number = forms.CharField(required=False)

	class Meta:
		model = MeterChange
		fields = ['flat', 'new_start_eb', 'new_start_dg', 'new_meter_sr']

	def save(self, commit=True):
		m = super(MeterChangeForm, self).save(commit=False)
		m.amt_left = m.flat.consumption.amt_left
		m.old_meter_sr = m.flat.meter_sr
		m.flat.meter_sr = m.new_meter_sr
		m.old_start_eb = m.flat.consumption.start_eb
		m.old_ng_eb = m.flat.consumption.ng_eb
		m.old_last_eb = m.flat.consumption.getLastEB()
		m.old_start_dg = m.flat.start_dg
		m.old_ng_dg = m.flat.ng_dg
		m.old_last_dg = m.flat.getLastDG()
		m.flat.consumption.start_eb = m.new_start_eb
		m.flat.consumption.start_dg = m.new_start_dg
		m.save()
		return m