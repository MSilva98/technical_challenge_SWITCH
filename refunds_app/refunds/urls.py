from django.urls import path
from . import views

app_name = 'refunds'
urlpatterns = [
    # /refunds/
    path('', views.listAllRefunds, name='allRefunds'),
    path('refund/<refund_id>/', views.showRefund, name='showRefund'),
    path('newRefund/<payment_id>', views.newRefund, name='newRefund'),
    path('refundedAmount/<payment_id>', views.refundedAmount, name='refundedAmount'),
    path('search/', views.filterView, name='searchRefunds'),
]