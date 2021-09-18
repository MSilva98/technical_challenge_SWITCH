from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    # /payments/
    path('', views.listAllPayments, name='allPayments'),
    path('payment/<payment_id>/', views.showPayment, name='showPayment'),
    path('newPayment/', views.newPayment, name='newPayment'),
    path('deletePayment/<payment_id>/', views.deletePayment, name='deletePayment'),
    path('settlePayment/<payment_id>/', views.settlePayment, name='settlePayment'),
    path('filterPayments/', views.filterPayments, name='filterPayments'),

    # Views that render a GUI
    path('allPayments/', views.listAllPaymentsGUI, name='allPaymentsGUI'),
    path('paymentGUI/<payment_id>/', views.showPaymentGUI, name='showPaymentGUI'),
    path('newPaymentGUI/', views.newPaymentGUI, name='newPaymentGUI'),
    path('processPayment/', views.processPayment, name='processPayment'),
    path('deletePaymentGUI/<payment_id>/', views.deletePaymentGUI, name='deletePaymentGUI'),
    path('settlePaymentGUI/<payment_id>/', views.settlePaymentGUI, name='settlePaymentGUI'),
    path('filterPaymentGUI/', views.filterPaymentsGUI, name='filterPaymentsGUI'),
]