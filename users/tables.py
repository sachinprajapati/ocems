from django.utils.timesince import timesince
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.html import escape

import django_tables2 as tables
from datetime import timedelta
import django_filters
import itertools

from .models import *

class NegativeFlatsTable(tables.Table):
    class Meta:
        model = Consumption
        fields = ("flat__tower", "flat__flat", "flat__owner", "deduction_status", "flat__phone", "amt_left", "last_deduction_dt")
        attrs = {"class": "table table-hover table-bordered table-sm"}

    def render_last_deduction_dt(self, value):
        now = timezone.localtime()
        difference = now-value
        if difference <= timedelta(minutes=1):
            return 'just now'
        if difference > timedelta(days=30):
            return value
        return '%(time)s ago' % {'time': timesince(value).split(', ')[0]}

# DEDUCTION_STATUS = [
#     ('', "All"),
#     (1, "N"),
#     (2, "Y")
# ]

class FlatsFilter(django_filters.FilterSet):
    amt_left__gt = django_filters.NumberFilter(field_name='amt_left', lookup_expr='gt')
    amt_left__lt = django_filters.NumberFilter(field_name='amt_left', lookup_expr='lt')
    # deduction_status = django_filters.ChoiceFilter(choices=DEDUCTION_STATUS)
    class Meta:
        model = Consumption
        fields = ['flat__tower',"deduction_status"]
        order_by = 'amt_left'

class FlatSMSTable(tables.Table):
    dt = tables.Column(verbose_name="Date & Time")
    class Meta:
        model = SentMessage
        fields = ("text", "dt")
        attrs = {"class": "table table-hover table-bordered table-sm"}

    def render_text(self, value):
        print("value is", value)
        return mark_safe('<span class="badge badge-light">%s</span>' % escape(value))