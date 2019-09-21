from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.utils import timezone

from .models import *
from .forms import RechargeForm
import json
import pytz

def dt_now():
	dt = timezone.now()
	utc = dt.replace(tzinfo=pytz.UTC)
	localtz = pytz.timezone("Asia/Calcutta")
	localtz = utc.astimezone(localtz)
	return localtz


@login_required()
def Dashboard(request):
	return render(request, 'users/dashboard.html', {})

# class RechargeView(CreateView):
# 	template_name = "users/recharge.html"
# 	form_class = RechargeForm


@login_required
def RechargeView(request):
	form = RechargeForm(request.POST or None)
	if request.method == "POST":
		print(dt_now())
		if form.is_valid():
			print(form)
		else:
			print(form.errors)
	context = {
		"form" : form,
	}
	return render(request, 'users/recharge.html', context)

@login_required()
def getFlat(request):
	if request.method == "POST":
		tower = request.POST.get("tower", '')
		flat = request.POST.get("flat", '')
		if tower and flat:
			flat = get_object_or_404(Flats, tower=tower, flat=flat)
			if flat:
				flatd = serializers.serialize('json', [flat, ])[1:-1]
				consumption = serializers.serialize('json', [flat.consumption, ])[1:-1]
				data = json.loads(flatd)['fields']
				consd = json.loads(consumption)['fields']
				for k,v in consd.items():
					data[k] = v
				return JsonResponse(data)
	return HttpResponse(status=404)



# @login_required()
# def NegativeBalanceFlats(request):
# 	context = {
# 		"flats": getNegativeFlats,
# 	}
# 	return render(request, 'users/negative-flats.html', context)


class NegativeBalanceFlats(ListView):
	model = Consumption
	template_name = "users/negative-flats.html"
	queryset = Consumption.objects.filter(amt_left__lt=0).order_by('flat__tower', 'flat__flat')


@login_required()
def getBillView(request):
	context = {}
	return render(request, 'users/getBill.html', context)


@login_required()
def DailyRechargeReport(request):
	context = {
		"args": {"type": "date", "name": "date"}
	}
	return render(request, 'users/rechargehistory.html', context)


@login_required()
def MonthlyRechargeReport(request):
	context = {
		"args": {"type": "month", "name": "month"}
	}
	return render(request, 'users/rechargehistory.html', context)