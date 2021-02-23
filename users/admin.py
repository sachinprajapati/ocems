from django.contrib import admin
from django import forms

from .models import *

@admin.register(Flats)
class FlatsAdmin(admin.ModelAdmin):
    ordering = ['tower', 'flat']
    search_fields = ['tower', 'flat']
    exclude = ('tower', 'flat')
    readonly_fields = ('user',)

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(tower=qs[0], flat=qs[1]), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    ordering = ['-dt']
    search_fields = ['tower', 'flat']

class ConsumptionAdmin(admin.ModelAdmin):
    list_filter = ('flat__tower', 'flat__flat')   # simple list filters
    ordering = ('flat__tower', 'flat__flat')
    search_fields = ('=flat__tower', '=flat__flat')
    readonly_fields = ('flat', 'meter_change_dt', 'deduction_status')
    exclude = ('last_deduction_dt', 'reset_dt', 'last_modified', 'ng_eb', 'ng_dg', 'ng_dt', 'dt')

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(flat__tower=qs[0], flat__flat=qs[1]), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False

class BillAdmin(admin.ModelAdmin):
    list_filter = ('year', 'month', 'flat__tower', 'flat__flat')
    ordering = ('-start_dt', 'flat__tower', 'flat__flat')
    search_fields = ('=flat__tower', '=flat__flat', "=month", "=year")
    readonly_fields = ('flat', 'month', 'year')

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(flat__tower=qs[0], flat__flat=qs[1], month=qs[2], year=qs[3]), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False

class MaintanceAdmin(admin.ModelAdmin):
    search_fields = ('flat__tower', 'flat__flat')
    readonly_fields = ('flat', 'dt')
    list_ordering = ('-dt', )

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(flat__tower=qs[0], flat__flat=qs[1]).order_by('-dt'), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False

class DebitAdmin(admin.ModelAdmin):
    readonly_fields = ('flat', )
    list_ordering = ('-dt', 'flat__tower', 'flat__flat')
    search_fields = ('=flat__tower', '=flat__flat')

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(flat__tower=qs[0], flat__flat=qs[1]).order_by('-dt'), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False

class RechargeAdmin(admin.ModelAdmin):
    list_filter = ('flat__tower', 'flat__flat')  # simple list filters
    ordering = ('-dt',)
    search_fields = ('=flat__tower', '=flat__flat')
    readonly_fields = ('flat', 'dt')
    exclude = ('last_deduction_dt', 'reset_dt', 'last_modified', 'ng_eb', 'ng_dg', 'ng_dt', 'dt')

    def get_search_results(self, request, queryset, search_term):
        if search_term and ',' in search_term:
            qs = search_term.split(',')
            return self.model.objects.filter(flat__tower=qs[0], flat__flat=qs[1]).order_by('-dt'), False
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

admin.site.register(Consumption, ConsumptionAdmin)
admin.site.register(Recharge, RechargeAdmin)
admin.site.register(MonthlyBill, BillAdmin)
admin.site.register(Maintance, MaintanceAdmin)
admin.site.register(DeductionAmt)
admin.site.register(MessageTemplate)
admin.site.register(SentMessage)
admin.site.register(Debit, DebitAdmin)
admin.site.register(OtherMaintance)
admin.site.register(PowerCut)

