from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users'

urlpatterns = [
	path('dashboard/', Dashboard, name="dashboard"),
	path('recharge/', RechargeView, name="recharge"),
	path("getFlat/", getFlat, name="getFlat"),
	path('bill/', getBillView, name="flat_bill"),
	path('negative-balance-flats/', NegativeBalanceFlats.as_view(), name="negative_balance_flats"),
	path('daily-recharge-report/', DailyRechargeReport, name="daily_recharge_report"),
    path('mothly-recharge-report/', MonthlyRechargeReport, name="monthly_recharge_report"),
]