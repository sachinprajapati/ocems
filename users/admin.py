from django.contrib import admin
from django import forms

from .models import *

@admin.register(Flats)
class FlatsAdmin(admin.ModelAdmin):
    ordering = ['tower', 'flat']
    search_fields = ['tower', 'flat']

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    ordering = ['-dt']
    search_fields = ['flat']


admin.site.register(Consumption)
admin.site.register(Recharge)
admin.site.register(MonthlyBill)
admin.site.register(Maintance)
admin.site.register(DeductionAmt)
admin.site.register(MessageTemplate)
admin.site.register(SentMessage)
admin.site.register(Debit)
admin.site.register(OtherMaintance)
admin.site.register(PowerCut)
