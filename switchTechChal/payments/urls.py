from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    # /payments/
    path('', views.listAll, name='allPayments'),
    path('payment/<payment_id>/', views.showPayment, name='showPayment'),
    path('newPayment/', views.newPayment, name='newPayment'),
    path('processPayment/', views.processPayment, name='processPayment'),
    path('deletePayment/<payment_id>/', views.deletePayment, name='deletePayment'),
    path('settlePayment/<payment_id>/', views.settlePayment, name='settlePayment'),
    path('searchByPaymentId/<payment_id>/', views.searchByPaymentId, name='searchByPaymentId'),
]