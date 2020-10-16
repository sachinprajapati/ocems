from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from datetime import datetime
import dateutil.relativedelta
from users.models import *
from .models import *
# Create your views here.


def ResidentRequired(function):
	def wrapper(request, *args, **kw):
		if request.user.is_staff or request.user.is_superuser:
			return redirect(reverse_lazy("users:dashboard"))
		else:
			if not request.session.get("flat"):
				return redirect(reverse_lazy("resident:select_flat"))
			return function(request, *args, **kw)
	return wrapper

@method_decorator(login_required, name="dispatch")
class SelectFlat(ListView):
	model = Flats
	template_name = "resident/select_flat.html"

	def get_queryset(self):
	    return self.request.user.flats_set.all()

@login_required
@ResidentRequired
def getRsBill(request):
	context = {
		"date": datetime.today() - dateutil.relativedelta.relativedelta(months=1)
	}
	context["errors"] = []
	if request.method == "POST":
		data = request.POST
		if data.get('month'):
			try:
				date = datetime.strptime(data['month'], "%Y-%m").date()
				bill = MonthlyBill.objects.get(month=date.month, year=date.year, flat__id=request.session["flat"])
				context = {
					"bill": bill,
					"date": date,
				}
				return render(request, 'users/bill_report.html', context)
			except Exception as e:
				print(e)
				context["errors"].append(e)
	return render(request, 'resident/bill.html', context)

@method_decorator(ResidentRequired, name='dispatch')
class RechargeHistory(LoginRequiredMixin, ListView):
	model = Recharge
	template_name = "resident/recharge_list.html"
	paginate_by = 20

	def get_queryset(self):
		return Recharge.objects.filter(flat__id = self.request.session["flat"]).order_by("-dt")

	def get_context_data(self, *args, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(*args, **kwargs)
		# Add in a QuerySet of all the books
		print(context)
		return context

@method_decorator(ResidentRequired, name='dispatch')
class ResidentProfile(LoginRequiredMixin, TemplateView):
	template_name = "resident/profile.html"

@login_required
def ActiveFlat(request, pk):
	try:
		flat = Flats.objects.get(pk=pk)
		request.session["flat"] = flat.pk
		return redirect(reverse_lazy("users:dashboard"))
	except Exception as e:
		print(e)
		return redirect(reverse_lazy("resident:select_flat"))

@login_required
def ChangePassword(request):
	form = PasswordChangeForm(request.POST or None)
	context = {"base": "base.html" if request.user.is_staff else "resident/base.html", "form": form}
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
		    user = form.save()
		    update_session_auth_hash(request, user)  # Important!
		    messages.success(request, 'Your password was successfully updated!')
		else:
		    messages.error(request, 'Please correct the error below.')
	return render(request, 'resident/change_password.html', context)

@method_decorator(ResidentRequired, name="dispatch")
class NoticeDetail(DetailView):
	model = Notice
	template_name = "resident/notice_detail.html"


@method_decorator(ResidentRequired, name='dispatch')
class CreateComplaint(SuccessMessageMixin, CreateView):
	model = Complaint
	fields = ('phone', 'remark')
	template_name = 'resident/create_form.html'
	success_url = reverse_lazy('resident:create_complaints')

	def form_valid(self, form):
		obj = form.save(commit=False)
		obj.flat_id = self.request.session["flat"]
		obj.save()
		messages.success(self.request, "Complaint Successfully Registered. Complaint Number {}".format(obj.id))
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['heading_title'] = 'Raise Complaint'
		return context

