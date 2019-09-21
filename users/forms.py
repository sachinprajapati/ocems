from django.forms import ModelForm
from .models import *


class RechargeForm(ModelForm):
	class Meta:
		model = Recharge
		fields = ['flat', 'recharge', 'Type', 'chq_dd', 'eb', 'dg']