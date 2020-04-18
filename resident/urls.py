from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'resident'

urlpatterns = [
	path('monthly-bill/', getRsBill, name="monthly_bill"),
	path('recharge-history/', RechargeHistory.as_view(), name="recharge_history"),
	path('profile/', ResidentProfile.as_view(), name="resident_profile"),
]