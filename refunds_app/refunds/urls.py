from django.urls import path
from . import views

app_name = 'refunds'
urlpatterns = [
    # /refunds/
    path('', views.listAllRefunds, name='allRefunds'),
    path('refund/<refund_id>/', views.showRefund, name='showRefund'),
    path('newRefund/', views.newRefund, name='newRefund'),
    path('search/', views.filterView, name='searchRefunds'),
]