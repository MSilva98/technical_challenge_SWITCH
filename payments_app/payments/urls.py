from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    # /payments/
    path('getAllPayments/', views.getAllPayments, name='getAllPayments'),
    path('getAllPaymentsID/', views.getAllPaymentsID, name='getAllPaymentsID'),
    path('', views.listAllPayments, name='allPayments'),
    path('payment/<payment_id>/', views.showPayment, name='showPayment'),
    path('getPayment/<payment_id>/', views.getPayment, name='getPayment'),
    path('newPayment/', views.newPayment, name='newPayment'),
    path('processPayment/', views.processPayment, name='processPayment'),
    path('deletePayment/<payment_id>/', views.deletePayment, name='deletePayment'),
    path('settlePayment/<payment_id>/', views.settlePayment, name='settlePayment'),
    path('search/', views.filterView, name='searchPayments'),
]