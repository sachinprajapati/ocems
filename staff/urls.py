from django.urls import path, include

from .views import *

app_name = 'staff'

urlpatterns = [
	path('meter-change/', MeterChangeView.as_view(), name="meter_change"),
	path('MeterChange/<int:pk>/', MeterChangeUpdate.as_view(), name='meter-update'),
]