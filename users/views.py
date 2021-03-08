from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Func, F
from django.db import connection
from django.contrib.auth.models import User
from django_tables2 import SingleTableView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from datetime import datetime, timedelta

from .models import *
from resident.models import *
from .forms import *
from .tables import *
import json
import pytz
import string 
import random
import dateutil.relativedelta
from dateutil import parser


class Homepage(TemplateView):
	template_name = "index.html"

def dt_now():
	dt = timezone.now()
	utc = dt.replace(tzinfo=pytz.UTC)
	localtz = pytz.timezone("Asia/Calcutta")
	localtz = utc.astimezone(localtz)
	return localtz

def AdminRequired(function):
	def wrapper(request, *args, **kw):
		if request.user.is_superuser and request.user.is_staff:
			return function(request, *args, **kw)
		else:
			return redirect(reverse_lazy("users:dashboard"))
	return wrapper

def StaffRequired(function):
    def wrapper(request, *args, **kw):
        if request.user.is_staff:
        	return function(request, *args, **kw)
        else:
            return redirect(reverse_lazy("users:dashboard"))
    return wrapper


def SessionFlat(function):
	def wrapper(request, *args, **kw):
		if not request.user.is_staff:
			flats = request.user.flats_set.all()
			if len(flats) == 1:
				request.session["flat"] = flats[0].pk
			elif len(flats) > 1:
				if not request.session.get("flat"):
					return HttpResponseRedirect(reverse_lazy("resident:select_flat"))
		return function(request, *args, **kw)
	return wrapper

@login_required
@SessionFlat
def Dashboard(request):
	if request.user.is_staff:
		return render(request, 'users/dashboard.html', {})
	else:
		return render(request, 'resident/dashboard.html', {})


@StaffRequired
def RechargeView(request):
	context = {}
	context['errors'] = []
	form = RechargeForm(request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			data = request.POST
			flat = Flats.objects.get(id=data['flat'])
			prevamt = flat.consumption.amt_left
			recharge = int(data['recharge'])
			if form.save():
				context = {
						"flat": flat,
						'recharge_amt' : recharge,
						"updated_bal" : prevamt+recharge,
						"prevamt": prevamt,
						"dt": timezone.localtime()
					}
				return render(request, "users/recharge_success.html", context)
	context['form'] = form
	return render(request, 'users/recharge.html', context)

@StaffRequired
def RechargeReceiptView(request):
	context = {
		"args": {"type": "month", "name": "month"},
		"flatrecharge": True,
		"url": reverse_lazy('users:recharge_receipt')
	}
	context['errors'] = []
	if request.method == "POST":
		data = request.POST
		fl = Flats.objects.get(id=data.get("id"))
		rch = Recharge.objects.filter(flat=fl).order_by("-dt")[0]
		context = {
			"flat": fl,
			'recharge_amt' : rch.recharge,
			"prevamt" : rch.amt_left,
			"updated_bal": rch.recharge+rch.amt_left,
			"dt": rch.dt
		}
		return render(request, "users/recharge_success.html", context)
	return render(request, 'users/rechargehistory.html', context)



@StaffRequired
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
				data["flat_no"] = flat.flat
				data["user"] = json.loads(serializers.serialize('json', [flat.user, ], fields=('username','is_active'))[1:-1])['fields'] if flat.user else False
				return JsonResponse(data)
	return HttpResponse(status=404)



# @login_required()
# def NegativeBalanceFlats(request):
# 	context = {
# 		"flats": getNegativeFlats,
# 	}
# 	return render(request, 'users/negative-flats.html', context)

@method_decorator(StaffRequired, name='dispatch')
class NegativeBalanceFlats(SingleTableMixin, FilterView):
	model = Consumption
	table_class = NegativeFlatsTable
	template_name = "users/list_view.html"
	queryset = Consumption.objects.filter().order_by('flat__tower', 'flat__flat')
	filterset_class = FlatsFilter
	paginate_by = 50

@method_decorator(StaffRequired, name="dispatch")
class PositiveBalanceFlats(ListView):
	model = Consumption
	template_name = "users/negative-flats.html"
	queryset = Consumption.objects.filter(amt_left__gt=0).order_by('flat__tower', 'flat__flat')

@method_decorator(StaffRequired, name="dispatch")
class NonDeductionFlats(ListView):
	model = Consumption
	template_name = "users/negative-flats.html"
	queryset = Consumption.objects.filter(deduction_status=1).order_by('flat__tower', 'flat__flat')

@method_decorator(StaffRequired, name="dispatch")
class FlatPowerCut(ListView):
	model = PowerCut
	template_name = "resident/power_cut.html"
	dt = datetime.today()
	queryset = PowerCut.objects.filter(dt__day=dt.day, dt__month=dt.month, dt__year=dt.year).order_by('flat__tower', 'flat__flat', '-dt')


@StaffRequired
def getBillView(request):
	context = {
		"date": datetime.today() - dateutil.relativedelta.relativedelta(months=1),
		"errors": []
	}
	if request.method == "POST":
		data = request.POST
		if data.get('flat') and data.get('month'):
			try:
				flat = Flats.objects.get(pk=data["flat"])
				date = parser.parse(data['month']).date()
				bill = MonthlyBill.objects.get(month=date.month, year=date.year, flat=flat)
				context = {
					"bill": bill,
					"date": date,
					"flat": flat,
				}
				return render(request, 'users/bill_report.html', context)
			except Exception as e:
				context = {
					"errors": []
				}
				print(e)
				context["errors"].append(e)
	print('context', context)
	return render(request, 'users/getBill.html', context)


@StaffRequired
def DailyRechargeReport(request):
	context = {
		"args": {"type": "date", "name": "date"}
	}
	if request.method == "POST":
		data = request.POST
		if data.get('date'):
			try:
				date = datetime.strptime(data['date'], "%Y-%m-%d").date()
				data = Recharge.objects.filter(dt__month=date.month, dt__year=date.year, dt__day=date.day).order_by("-dt")
				total = data.aggregate(Sum('recharge'))
				context = {
					"recharge" : data,
					"total": total,
				}
			except Exception as e:
				print(e)
				context['error'] = e
	return render(request, 'users/rechargehistory.html', context)


@StaffRequired
def MonthlyRechargeReport(request):
	context = {
		"args": {"type": "month", "name": "month"}
	}
	if request.method == "POST":
		data = request.POST
		if data.get('month'):
			try:
				date = datetime.strptime(data['month'], "%Y-%m").date()
				data = Recharge.objects.filter(dt__month=date.month, dt__year=date.year).annotate(dtdate=Func(F('dt__day'), function='date')).values('dtdate').annotate(sum=Sum('recharge'), count=Count('recharge'))
				context = {
					"recharge" : data,
					"total": sum([i['sum'] for i in data]),
					"count": sum([i['count'] for i in data]),
					"month": True,
				}
			except Exception as e:
				context['error'] = e
	return render(request, 'users/rechargehistory.html', context)


@StaffRequired
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
				recharge = Recharge.objects.filter(flat__id=flat_pkey).order_by("dt")
				total = recharge.aggregate(Sum('recharge'))
				context = {
					"recharge": recharge,
					"total": total,
				}
			except Exception as e:
				print(e)
	return render(request, 'users/rechargehistory.html', context)


@StaffRequired
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


@StaffRequired
def FlatMaintanceReport(request):
	context = {
		"form" : True,
		"title": "Flat Maintance Report",
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

@StaffRequired
def FlatSMSReport(request):
	context = {
		"form" : True,
		"title": "Flat SMS Report",
	}
	if request.method == "POST":
		data = request.POST
		if data.get("start-date") and data.get("end-date") and data.get("id"):
			sdate = datetime.strptime(data['start-date'], "%Y-%m-%d").date()
			edate = datetime.strptime(data['end-date'], "%Y-%m-%d").date() + timedelta(days=1)
			sms = SentMessage.objects.filter(flat__id=data['id'], dt__range=(sdate, edate)).order_by('dt')
			context = {
				"table" : FlatSMSTable(sms),
				"flat": Flats.objects.get(id=data['id']),
			}
			return render(request, 'users/list_view.html', context)
	return render(request, 'users/maintance_report.html', context)

@method_decorator(StaffRequired, name='dispatch')
class SendSMSView(SuccessMessageMixin, FormView):
	template_name = 'users/send_sms.html'
	form_class = SendSMSForm
	success_url = '/send-sms/'
	success_message = 'Sent Message to %(flat_id)s'



@method_decorator(AdminRequired, name="dispatch")
class MeterChangeView(SuccessMessageMixin, CreateView):
	template_name = 'users/meterchange.html'
	form_class = MeterChangeForm
	success_url = reverse_lazy('users:meter_change')
	success_message = "%(flat)s's Meter Changed Successfully"


def BillAdjusmentView(request):
	context = {
		"args": {"type": "month", "name": "month"},
		"choose_date": True
	}
	if request.method == "POST":
		data = request.POST
		if data.get('month'):
			try:
				date = datetime.strptime(data['month'], "%Y-%m").date()
				cursor = connection.cursor()
				sql = ('''SELECT * FROM
					(SELECT (opn_amt-(((end_eb-start_eb)*eb_price)+((end_dg-start_dg)*dg_price)) +
						(select sum(recharge) from users_recharge as rc where 
							EXTRACT(MONTH FROM rc.dt) = {0} and EXTRACT(YEAR FROM rc.dt) = {1} and flat_id=bill.flat_id
						) - (select sum(mcharge)+sum(famt) from users_maintance as mc where 
							EXTRACT(MONTH FROM mc.dt) = {0} and EXTRACT(YEAR FROM mc.dt) = {1} and flat_id=bill.flat_id
						) - (select sum(debit_amt) from users_debit as ud where 
							EXTRACT(MONTH FROM ud.dt) = {0} and EXTRACT(YEAR FROM ud.dt) = {1} and flat_id=bill.flat_id
						))-cls_amt
						AS Adjustment, flat_id	, flat.tower, flat.flat
					  FROM public.users_monthlybill as bill inner join public.users_flats as flat 
					  on bill.flat_id = flat.id
					  where bill.month={0} and bill.year={1} order by flat.tower, flat.flat
					) as innerTable WHERE Adjustment IS NOT NULL and Adjustment NOT BETWEEN -1 and 1'''.format(date.month, date.year))
				cursor.execute(sql)
				row = cursor.fetchall()
				context["object_list"] = row
				context["choose_date"] = False
				context["date"] = date
			except Exception as e:
				context['error'] = e
	return render(request, 'users/bill_adjustment.html', context)

@method_decorator(AdminRequired, name="dispatch")
class TowerListView(SuccessMessageMixin, ListView):
	model = DeductionAmt


@method_decorator(AdminRequired, name="dispatch")
class TowerUpdateView(SuccessMessageMixin, UpdateView):
	model = DeductionAmt
	fields = ['eb_price', 'dg_price']


@StaffRequired
def CreateLogin(request):
	context = {}
	context['errors'] = []
	if request.method == "POST":
		data = request.POST
		try:
			flat = Flats.objects.get(pk=data["flat"])
			if not str(flat.tower) == data.get("tower") or not str(flat.flat) == data.get("flat-no") or flat.user is not None:
				raise Exception("Flat not Found or Already Registered")
			if flat.email is None:
				raise Exception("No Phone or Email registered for {}/{}".format(flat.tower, flat.flat))
			pwd = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
			try:
				user = User.objects.get(username=flat.email)
				msg = 'Hello {} you have successfully registered for login {}/{} with existing account {}'.format(flat.owner, \
			    	flat.tower, flat.flat, user.username)
			except:
				user = User(username=flat.email)
				user.set_password(pwd)
				user.save()
				msg = 'Hello {} you have successfully registered for login {}/{} with email "{}" and password {}'.format(flat.owner, \
			    	flat.tower, flat.flat, flat.email, pwd)
			flat.user = user
			flat.save()
			send_mail(
			    'Flat Login Registration',
			    msg,
			    'from@example.com',
			    [flat.email],
			    fail_silently=False,
			)
			context["message"] = "Sucessfully Registered {}/{} with email {}".format(flat.tower, flat.flat, user.username)
		except Exception as e:
			print("na ji", data)
			context["errors"].append(e)
	return render(request, 'users/create-login.html', context)

@StaffRequired
def UpdateLogin(request):
	context = {}
	context['errors'] = []
	if request.method == "POST":
		data = request.POST
		try:
			flat = get_object_or_404(Flats, pk=data["flat"])
			if str(flat.tower) != data.get("tower") or str(flat.flat) != data.get("flat-no") or flat.user is None:
				raise Exception("Flat not Found")
			if data.get("status"):
				flat.user.is_active = data["status"]
				flat.user.save()
				context["message"] = "Sucessfully Login Status Changed for {}/{}".format(flat.tower, flat.flat)
		except Exception as e:
			print("na ji", data, e)
			context["errors"].append(e)
	return render(request, 'users/update_login.html', context)


@method_decorator(AdminRequired, name="dispatch")
class DebitView(SuccessMessageMixin, CreateView):
	model = Debit
	fields = ["flat", "debit_amt", "remarks"]
	success_url = reverse_lazy('users:debit')
	success_message = "%(debit_amt)s successfully debited from %(flat)s"

	def form_valid(self, form):
		cons = Consumption.objects.get(flat=form.instance.flat)
		form.instance.eb = cons.eb
		form.instance.dg = cons.dg
		form.instance.amt_left = float(cons.amt_left)
		cons.amt_left -= form.instance.debit_amt
		cons.save()
		return super().form_valid(form)

@StaffRequired
def SMSReport(request):
	context = {
		"args": {"type": "date", "name": "date"}
	}
	if request.method == "POST":
		data = request.POST
		if data.get('date'):
			try:
				date = datetime.strptime(data['date'], "%Y-%m-%d").date()
				data = SentMessage.objects.filter(dt__month=date.month, dt__year=date.year, dt__day=date.day).order_by("flat__tower", "flat__flat")
				total = len(data)
				context = {
					"recharge" : data,
					"total": total,
				}
			except Exception as e:
				print(e)
				context['error'] = e
	return render(request, 'users/smshistory1.html', context)

@AdminRequired
def SelectFlat(request):
	context = {}
	if request.method == 'POST':
		try:
			flat = Flats.objects.get(tower=request.POST["tower"], flat=request.POST["flat-no"])
			return redirect(reverse_lazy('users:admin_update_flat', kwargs={'pk': flat.id}))
		except Exception as e:
			context["errors"] = [e]
	return render(request, 'users/select_flat.html', context)


@method_decorator(AdminRequired, name="dispatch")
class UpdateFlatView(SuccessMessageMixin, UpdateView):
	model = Flats
	fields = ['owner', 'phone', 'email']
	success_url = reverse_lazy('users:admin_select_flats')

	def get_success_message(self, cleaned_data):
	    return "Successfully Updated %(tower)s / %(flat)s" % {'tower': self.object.tower, 'flat': self.object.flat}


@method_decorator(StaffRequired, name="dispatch")
class CreateNotice(SuccessMessageMixin, CreateView):
	model = Notice
	fields = ('sub', 'text')
	template_name = 'users/flats_form.html'
	success_message = "Notice Successfully Created"
	success_url = reverse_lazy('users:create_notice')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['heading_title'] = 'Create Notice'
		return context


@method_decorator(StaffRequired, name='dispatch')
class NoticeList(ListView):
	model = Notice
	template_name = "users/notice_list.html"
	queryset = Notice.objects.filter().order_by('-dt')


@method_decorator(StaffRequired, name='dispatch')
class ActiveNoticeList(ListView):
	model = Notice
	template_name = "users/notice_list.html"
	queryset = Notice.objects.filter(status=1).order_by('-dt')

@method_decorator(StaffRequired, name='dispatch')
class NoticeUpdate(UpdateView):
	model = Notice
	fields = ('sub', 'status', 'text')
	success_message = 'Notice Successfully Updated'
	template_name = "users/flats_form.html"
	success_url = reverse_lazy("users:notice_list")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['heading_title'] = 'update Notice'
		return context
	
	
@method_decorator(StaffRequired, name="dispatch")
class ComplaintList(ListView):
	model = Complaint
	template_name = 'users/complaint_list.html'

	def get_queryset(self):
		return Complaint.objects.filter(status=self.kwargs['status'])



@staff_member_required
def SendSmsToAll(request):
	form = MyForm(request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			print(form.cleaned_data["towers"])
	return render(request, 'users/send_sms_to_all.html', {'forms': form})
