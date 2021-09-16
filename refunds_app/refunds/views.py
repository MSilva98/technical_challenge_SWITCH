from django.contrib import messages
from django.http import response
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control
from .models import Refund, RefundForm
import requests
import datetime

# Payments microservice URL
payments_url = 'http://172.26.1.1:1111/api/payments/'
global refundTimeout 
refundTimeout = 30

def is_valid_queryparam(param):
    return param != '' and param is not None

def listAllRefunds(request):
    global refundTimeout
    allRefunds = Refund.objects.all()
    t = request.GET.get('timeout')
    if is_valid_queryparam(t):
        refundTimeout = t
        print("\n\n\nTIMEOUT RESET: " + str(refundTimeout))
    return render(request, 'refunds/allRefunds.html', {'allRefunds': allRefunds, 'payments_url': payments_url, 'refundTimeout': refundTimeout})

def getTotalAmount(payment_id):
    refunds = Refund.objects.filter(payment_id=payment_id)
    amount = 0
    for refund in refunds:
        amount += refund.amount
    return amount

def refundedAmount(request, payment_id):
    return response.JsonResponse({'refunded_amount': getTotalAmount(payment_id)})

def refundTimePassed(payment_date):
    global refundTimeout
    date, time = payment_date.split('T')
    y,m,d = date.split('-')
    h,mn,s = time[:-4].split(':')
    creation_date = datetime.datetime(int(y),int(m),int(d),int(h),int(mn),int(s))
    date_now = datetime.datetime.now()
    delta = datetime.timedelta(minutes=refundTimeout)
    return date_now-delta > creation_date

@cache_control(no_cache=True,smust_validate=True,no_store=True)
def newRefund(request, payment_id):
    global refundTimeout
    # Request Payments API information on payment with payment_id
    r = requests.get(payments_url+'getPayment/'+payment_id)
    if r.status_code == 200:
        payment = r.json()
        payment_date = payment['created_at']
        if refundTimePassed(payment_date):
            return response.HttpResponse('Payments cannot be refunded after ' + str(refundTimeout) + " minutes of the creation date.")
        totalPaid = getTotalAmount(payment_id)
        remaining_amount = payment['amount']-totalPaid
        if remaining_amount > 0:
            form = RefundForm(request.POST or None)
            if form.is_valid():
                # all refunds associated with this payment_id + payment that will be done now can't surpass the payment amount
                if totalPaid+float(form['amount'].value()) > payment['amount']:
                    messages.info(request, 'Cannot create a new refund with that amount. Max amount is: ' + str(payment['amount']-totalPaid))
                    return render(request, 'refunds/createRefund.html', {'form': form, 'payment_id': payment_id, 'remaining_amount': remaining_amount})  
                form.save()
                return redirect(payments_url+'payment/'+payment_id)
            return render(request, 'refunds/createRefund.html', {'form': form, 'payment_id': payment_id, 'remaining_amount': remaining_amount})
        else:
            return redirect(payments_url+'payment/'+payment_id)

def filter(request):
    refunds = Refund.objects.all()
    refund_id = request.GET.get('refund_id')
    payment_id = request.GET.get('payment_id')

    if is_valid_queryparam(refund_id) and refund_id != "Choose...":
        refunds = refunds.filter(refund_id=refund_id)
    
    if is_valid_queryparam(payment_id) and payment_id != "Choose...":
        refunds = refunds.filter(payment_id=payment_id)

    return refunds

def filterView(request):
    all_refund_ids = list(Refund.objects.all().values_list('refund_id', flat=True))
    all_payment_ids = list(Refund.objects.all().values_list('payment_id', flat=True).distinct())
    return render(request, 'refunds/filterRefunds.html', {'refunds': filter(request), 'refund_ids': all_refund_ids, 'payment_ids': all_payment_ids})

def paymentToString(payment):
    return 'Payment ID:' + payment['payment_id'] + ", Amount: " + str(payment['amount']) + "€, Method: " + payment['payment_method'] + ", Status: " + payment['status'] + ", Created at: " + payment['created_at'] + "\n" 

def showRefund(request, refund_id):
    refund = get_object_or_404(Refund, refund_id=refund_id)
    r = requests.get(payments_url+'getPayment/'+refund.payment_id)
    if r.status_code == 200:
        data = r.json()
        return render(request, 'refunds/showRefund.html', {'refund_id': refund_id, 'refund': refund, 'payment': paymentToString(data)})
    return response.HttpResponseServerError("Could not access payments service!")