from django.contrib import messages
from django.http import response
from django.shortcuts import get_object_or_404, redirect, render
from .models import Refund, RefundForm
import requests

# Payments URL
# url = 'http://127.0.0.1:1111/api/payments/'
url = 'http://127.0.0.1:8000/api/payments/'

def listAllRefunds(request):
    allRefunds = Refund.objects.all()
    return render(request, 'refunds/allRefunds.html', {'allRefunds': allRefunds, 'payments_url': url})

def getTotalAmount(payment_id):
    refunds = Refund.objects.filter(payment_id=payment_id)
    amount = 0
    for refund in refunds:
        amount += refund.amount
    return amount

def newRefund(request):
    # Request Payments API all payments
    r = requests.get(url+'getAllPayments/')
    refundedPayments = Refund.objects.values_list('payment_id', flat=True)
    if r.status_code == 200:
        allPayments = r.json()['payments']
        # tupple with payment_id and remainig amount according to previous refunds
        payment_amount = []
        for p in allPayments:
            p_id = p['payment_id']
            remainder = p['amount']-getTotalAmount(p_id)
            if remainder > 0:
                payment_amount.append((p_id, remainder))

        form = RefundForm(request.POST or None)
        if form.is_valid():
            choosenPaymentID = form['payment_id'].value()
            if choosenPaymentID in refundedPayments:
                totalPaid = getTotalAmount(choosenPaymentID)
                for p in allPayments:
                    if p['payment_id'] == choosenPaymentID:
                        # all refunds associated with this payment_id + the payment that will be done now can't surpass the payment amount
                        if totalPaid+float(form['amount'].value()) > p['amount']:
                            messages.info(request, 'Cannot create a new refund with that amount. Max amount is: ' + str(p['amount']-totalPaid))
                            return render(request, 'refunds/createRefund.html', {'form': form, 'payment_amount': payment_amount})  
            form.save()
            return redirect('refunds:allRefunds')
        return render(request, 'refunds/createRefund.html', {'form': form, 'payment_amount': payment_amount})
    else:
        return response.Http404('Could not find any payment.')

def is_valid_queryparam(param):
    return param != '' and param is not None

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
    return 'Payment ID:' + payment['payment_id'] + ", Amount: " + str(payment['amount']) + "€, Method: " + payment['payment_method'] + ", Status: " + payment['status'] + "\n" 

def showRefund(request, refund_id):
    refund = get_object_or_404(Refund, refund_id=refund_id)
    r = requests.get(url+'getPayment/'+refund.payment_id)
    if r.status_code == 200:
        data = r.json()
    return render(request, 'refunds/showRefund.html', {'refund_id': refund_id, 'refund': refund, 'payment': paymentToString(data)})