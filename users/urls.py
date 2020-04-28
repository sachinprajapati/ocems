from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users'

urlpatterns = [
	path('', Homepage.as_view(), name="homepage"),
	path('dashboard/', Dashboard, name="dashboard"),
	path('recharge/', RechargeView, name="recharge"),
	path('recharge-receipt/', RechargeReceiptView, name="recharge_receipt"),
	path("getFlat/", getFlat, name="getFlat"),
	path('bill/', getBillView, name="flat_bill"),
	path('flat-recharge-report/', FlatRechargeReport, name="flat_recharge_report"),
	path('flat-sms-report/', FlatSMSReport, name="flat_sms_report"),
	path('flat-hourly-report/', FlatHourlyReport, name="flat_hourly_report"),
	path('flat-maintance-report/', FlatMaintanceReport, name="flat_maintance_report"),
	path('negative-balance-flats/', NegativeBalanceFlats.as_view(), name="negative_balance_flats"),
	path('positive-balance-flats/', PositiveBalanceFlats.as_view(), name="positive_balance_flats"),
	path('non-deduction-flats/', NonDeductionFlats.as_view(), name="non_deduction_flats"),
	path('daily-recharge-report/', DailyRechargeReport, name="daily_recharge_report"),
    path('mothly-recharge-report/', MonthlyRechargeReport, name="monthly_recharge_report"),
	path('send-sms/', SendSMSView.as_view(), name="send_sms"),
	path('meter-change/', MeterChangeView.as_view(), name="meter_change"),
	path('bill-adjustment/', BillAdjusmentView, name="bill_adjustment"),
	path('tower-list/', TowerListView.as_view(), name="tower_list"),
	path('tower-update/<int:pk>/', TowerUpdateView.as_view(), name="tower_update"),
	#path('Change-Mantance/', UpdateMaintanceView.as_view(), name="change_maintance"),
	path('debit/', DebitView.as_view(), name="debit"),
	path('sms-report/', SMSReport, name="sms_report"),
	path('create-login/', CreateLogin, name="create_login"),
	path('update-login/', UpdateLogin, name="update_login"),
	#path('design/', Design, name="design"),
]