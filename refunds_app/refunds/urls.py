from django.urls import path
from . import views

app_name = 'refunds'
urlpatterns = [
    # /refunds/
    path('', views.listAllRefunds, name='allRefunds'),
    path('setRefundTimeout/', views.setRefundTimeout, name='setRefundTimeout'),
    path('refund/<refund_id>/', views.showRefund, name='showRefund'),
    path('newRefund/<payment_id>', views.newRefund, name='newRefund'),
    path('filterRefunds/', views.filterRefunds, name='filterRefunds'),

    # Views that render a GUI
    path('allRefunds/', views.listAllRefundsGUI, name='allRefundsGUI'),
    path('refundGUI/<refund_id>/', views.showRefundGUI, name='showRefundGUI'),
    path('newRefundGUI/<payment_id>', views.newRefundGUI, name='newRefundGUI'),
    path('filterRefundsGUI/', views.filterRefundsGUI, name='filterRefundsGUI'),
]