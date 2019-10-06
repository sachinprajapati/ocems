from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator

@method_decorator(staff_member_required, name='dispatch')
class MeterChangeView(TemplateView):
    template_name = 'staff/meter_change.html'


@method_decorator(staff_member_required, name='dispatch')
class MeterChangeUpdate(TemplateView):
    template_name = 'staff/meter_update.html'
