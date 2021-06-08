from django.forms import ModelForm
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import *
from .tasks import *
from ocems.settings import conn
import csv


class RechargeForm(ModelForm):
	class Meta:
		model = Recharge
		fields = ['flat', 'recharge', 'Type', 'chq_dd']

	def clean_recharge(self):
		recharge = self.cleaned_data['recharge']
		if recharge < 500:
			raise ValidationError("Recharge Amount should be more thann 500")
		return recharge


	def save(self, commit=True):
		m = super(RechargeForm, self).save(commit=False)
		obj = Consumption.objects.get(flat=m.flat)
		m.amt_left = obj.amt_left
		obj.amt_left += m.recharge
		m.eb = obj.eb
		m.dg = obj.dg
		obj.status = getConsumptionStatus(obj.amt_left)
		obj.save()
		m.save()
		return m

class SendSMSForm(forms.Form):
	flat_id = forms.IntegerField()
	message = forms.CharField(widget=forms.Textarea())
	balinfo = forms.BooleanField()

	def clean_flat_id(self):
		try:
			flat = Flats.objects.get(id=self.cleaned_data['flat_id'])
		except Exception as e:
			raise ValidationError(e)
		return flat
	
	def clean_balinfo(self):
		flat = self.cleaned_data['flat_id']
		bal = self.cleaned_data['balinfo']
		if bal:
			# text = "Hi {} your balance is {} of tower {} and flat {}".format(flat.owner, flat.consumption.amt_left, flat.tower, flat.flat)
			# SendSMS(text, flat)
			mt = MessageTemplate.objects.get(m_type=4)
			text = mt.text.format(flat.owner, flat.consumption.amt_left, flat.tower, flat.flat)
			mt.sendMessage(text, flat)
		return bal


class MeterChangeForm(ModelForm):

	class Meta:
		model = MeterChange
		fields = ['flat', 'new_start_eb', 'new_start_dg', 'new_meter_sr']

	def save(self, commit=True):
		m = super(MeterChangeForm, self).save(commit=False)
		try:
			with transaction.atomic():
				m.amt_left = m.flat.consumption.amt_left
				m.old_meter_sr = m.flat.meter_sr
				m.flat.meter_sr = m.new_meter_sr
				m.flat.save()
				m.old_start_eb = m.flat.consumption.start_eb
				m.old_ng_eb = m.flat.consumption.ng_eb
				m.old_last_eb = m.flat.consumption.getLastEB()
				m.old_start_dg = m.flat.consumption.start_dg
				m.old_ng_dg = m.flat.consumption.ng_dg
				m.old_last_dg = m.flat.consumption.getLastDG()
				m.flat.consumption.start_eb = m.new_start_eb
				m.flat.consumption.start_dg = m.new_start_dg
				m.flat.consumption.ng_eb = 0
				m.flat.consumption.ng_dg = 0
				m.flat.consumption.eb = 0
				m.flat.consumption.dg = 0
				m.flat.consumption.meter_change_dt = timezone.now()
				m.flat.consumption.save()
				m.save()
				return m
		except Exception as e:
			print(e)
			return False

APPROVAL_CHOICES = [(i.pk, i.tower) for i in DeductionAmt.objects.filter().order_by("tower")]

# class MyForm(forms.Form):
# 	towers = forms.MultipleChoiceField(choices=APPROVAL_CHOICES, widget=forms.CheckboxSelectMultiple())
# 	message = forms.Textarea()

class BulkDebitForm(forms.ModelForm):
	file = forms.FileField()
	remarks = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols': 4 }))
	class Meta:
		model = Debit
		fields = ('remarks', )

	def save(self):
		m = super(BulkDebitForm, self).save(commit=False)
		file = csv.reader(self.cleaned_data['file'])
		dl = [Debit()]
		return m

