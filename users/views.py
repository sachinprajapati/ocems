from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.core import serializers
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Sum
from django.utils import timezone

from datetime import datetime, timedelta

from .models import *
from .forms import *
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
	context = {}
	context['errors'] = []
	form = RechargeForm(request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			data = request.POST
			flat = Flats.objects.get(id=data['flat'])
			recharge = int(data['recharge'])
			if form.save():
				context = {
						"flat": flat,
						'recharge_amt' : recharge,
						"prevamt" : flat.consumption.amt_left-recharge,
					}
				return render(request, "users/recharge_success.html", context)
			else:
				context['errors'].append("Recharge Failed")
	context['form'] = form
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

class NonDeductionFlats(ListView):
	model = Consumption
	template_name = "users/negative-flats.html"
	queryset = Consumption.objects.filter(deduction_status=1).order_by('flat__tower', 'flat__flat')


@login_required()
def getBillView(request):
	context = {}
	if request.method == "POST":
		data = request.POST
		if data.get('flat') and data.get('month'):
			flat = get_object_or_404(Flats, pk=data["flat"])
			date = datetime.strptime(data['month'], "%Y-%m").date()
			bill = MonthlyBill.objects.get(month=date.month, year=date.year, flat=flat)
			context = {
				"bill": bill,
				"date": date,
				"report_date": datetime.today(),
				"flat": flat,
			}
			return render(request, 'users/bill_report.html', context)
	return render(request, 'users/getBill.html', context)


@login_required()
def DailyRechargeReport(request):
	context = {
		"args": {"type": "date", "name": "date"}
	}
	if request.method == "POST":
		data = request.POST
		if data.get('date'):
			try:
				date = datetime.strptime(data['date'], "%Y-%m-%d").date()
				data = Recharge.objects.filter(dt__month=date.month, dt__year=date.year, dt__day=date.day)
				total = data.aggregate(Sum('recharge'))
				context = {
					"recharge" : data,
					"total": total,
				}
			except Exception as e:
				print(e)
				context['error'] = e
	return render(request, 'users/rechargehistory.html', context)


@login_required()
def MonthlyRechargeReport(request):
	context = {
		"args": {"type": "month", "name": "month"}
	}
	if request.method == "POST":
		data = request.POST
		if data.get('month'):
			try:
				date = datetime.strptime(data['month'], "%Y-%m").date()
				data = Recharge.objects.filter(dt__month=date.month, dt__year=date.year)
				total = data.aggregate(Sum('recharge'))
				context = {
					"recharge" : data,
					"total": total,
				}
			except Exception as e:
				context['error'] = e
	return render(request, 'users/rechargehistory.html', context)


@login_required()
def FlatRechargeReport(request):
	context = {
		"args": {"type": "month", "name": "month"},
		"flatrecharge": True,
	}
	if request.method == "POST":
		flat_pkey = request.POST.get("id", "")
		print("flat_pkey is ", flat_pkey)
		if flat_pkey:
			try:
				recharge = Recharge.objects.filter(flat__id=flat_pkey)
				total = recharge.aggregate(Sum('recharge'))
				context = {
					"recharge": recharge,
					"total": total,
				}
			except Exception as e:
				print(e)
	return render(request, 'users/rechargehistory.html', context)


@login_required()
def FlatHourlyReport(request):
	context = {
		"form" : True,
	}
	if request.method == "POST":
		data = request.POST
		if data.get("start-date") and data.get("end-date") and data.get("id"):
			sdate = datetime.strptime(data['start-date'], "%Y-%m-%d").date()
			edate = datetime.strptime(data['end-date'], "%Y-%m-%d").date() + timedelta(days=1)
			readings = Reading.objects.filter(flat__id=data['id'], dt__range=(sdate, edate)).order_by('dt')
			context = {
				"readings" : readings,
				"flat": Flats.objects.get(id=data['id'])
			}
	return render(request, 'users/flats-hourly-report.html', context)


@login_required
def FlatMaintanceReport(request):
	context = {
		"form" : True,
	}
	if request.method == "POST":
		data = request.POST
		if data.get("start-date") and data.get("end-date") and data.get("id"):
			sdate = datetime.strptime(data['start-date'], "%Y-%m-%d").date()
			edate = datetime.strptime(data['end-date'], "%Y-%m-%d").date() + timedelta(days=1)
			mt = Maintance.objects.filter(flat__id=data['id'], dt__range=(sdate, edate)).order_by('dt')
			context = {
				"maintance" : mt,
				"flat": Flats.objects.get(id=data['id'])
			}
	return render(request, 'users/maintance_report.html', context)


class SendSMSView(LoginRequiredMixin, SuccessMessageMixin, FormView):
	template_name = 'users/send_sms.html'
	form_class = SendSMS
	success_url = '/send-sms/'
	success_message = 'Sent Message to %(id)s'

	def form_valid(self, form):
		form.send_email()
		return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class MeterChangeView(SuccessMessageMixin, CreateView):
	template_name = 'users/meterchange.html'
	form_class = MeterChangeForm
	success_url = reverse_lazy('users:meter_change')
	success_message = "%(flat)s's Meter Changed Successfully"

@method_decorator(staff_member_required, name='dispatch')
class BillAdjusmentView(SuccessMessageMixin, ListView):
	template_name = 'users/bill_adjustment.html'
	success_url = reverse_lazy('users:meter_change')
	success_message = "%(flat)s's Meter Changed Successfully"
	model = MonthlyBill
	# paginate_by = 10

	def get_queryset(self):
		try:
			date = datetime.strptime(self.request.GET.get('month'), "%Y-%m").date()
			print("date is ", date)
			result = [i for i in MonthlyBill.objects.filter(year=date.year, month=date.month) if i.get_Adjustment() < 0]
		except Exception as e:
			print(e)
			return None
		return result

	# def get_context_data(self, **kwargs):
	# 	context = super().get_context_data(**kwargs)
	# 	if not self.request.GET.get('month'):
	# 		context["choose_date"] = True
	# 	print(len(context['object_list']))
	# 	return context