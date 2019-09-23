from django.contrib import admin

from .models import *

@admin.register(Flats)
class FlatsAdmin(admin.ModelAdmin):
    ordering = ['tower', 'flat']
    search_fields = ['tower', 'flat']


admin.site.register(Consumption)
admin.site.register(Recharge)
admin.site.register(MonthlyBill)
admin.site.register(Maintance)
admin.site.register(Reading)
