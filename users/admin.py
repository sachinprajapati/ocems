from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.http import HttpResponse

from .models import *
from .forms import ChangeMeterForm


# class MyAdminSite(AdminSite):

#      def get_urls(self):
#          from django.urls import path
#          urls = super().get_urls()
#          urls += [
#              path('my_view/', self.admin_view(self.my_view))
#          ]
#          return urls

#      def my_view(self, request):
#          return HttpResponse("Hello!")

# admin_site = MyAdminSite()

class FlatsAdmin(admin.ModelAdmin):
    ordering = ['tower', 'flat']
    search_fields = ['tower', 'flat']
    readonly_fields=('tower', 'flat', 'flat_size')


class ReadingAdmin(admin.ModelAdmin):
    ordering = ['-dt']
    search_fields = ['flat']


class ConsumptionAdmin(admin.ModelAdmin):
    ordering = ['flat__tower', 'flat__flat']
    search_fields = ['flat__tower', 'flat__flat']
    readonly_fields=('dt', 'flat', 'ng_dt', 'last_deduction_dt')


class DeductionAmtAdmin(admin.ModelAdmin):
    ordering = ['tower']
    readonly_fields=('tower',)

class ChangeMeterAdmin(admin.ModelAdmin):
    form = ChangeMeterForm
    ordering = ['flat__tower', 'flat__flat']
    search_fields = ['flat__tower', 'flat__flat']
    readonly_fields=('dt', 'flat', 'ng_dt', 'last_deduction_dt')

    def save_model(self, request, obj, form, change):
        print("obj is",obj)
        print("form is", form)
        super().save_model(request, obj, form, change)

admin.site.register(Flats, FlatsAdmin)
admin.site.register(Reading, ReadingAdmin)
#admin_site.register(Consumption, ConsumptionAdmin)
admin.site.register(DeductionAmt, DeductionAmtAdmin)
admin.site.register(Recharge)
admin.site.register(MonthlyBill)
admin.site.register(Maintance)
admin.site.register(Consumption, ChangeMeterAdmin)
admin.site.register(MeterChange)
admin.site.register(Feeder)
