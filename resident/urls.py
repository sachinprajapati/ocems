from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'resident'

urlpatterns = [
	path('monthly-bill/', getRsBill, name="monthly_bill"),
	path('recharge-history/', RechargeHistory.as_view(), name="recharge_history"),
	path('profile/', ResidentProfile.as_view(), name="resident_profile"),
	path('select-flat/', SelectFlat.as_view(), name="select_flat"),
	path('active-flat/<int:pk>/', ActiveFlat, name="active_flat"),
	path('change-password/', ChangePassword, name="change_password"),
]