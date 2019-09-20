from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users'

urlpatterns = [
	path('dashboard/', Dashboard, name="dashboard"),
	path('recharge/', Recharge, name="recharge"),
	path("getFlat/", getFlat, name="getFlat"),
]