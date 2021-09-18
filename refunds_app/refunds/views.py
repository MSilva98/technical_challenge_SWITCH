from django.contrib import messages
from django.forms.models import model_to_dict
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from .models import Refund, RefundForm
from kafka import KafkaConsumer
import pickle
import datetime

# Payments microservice URL (only used in GUI version to redirect to showPayment page)
payments_url = 'http://172.26.1.1:1111/api/payments/'

# Kafka URL
kafka_server = 'kafka:9092'

# global variable
# Refunds can only be commited after refundTimeout minutes after receiving the request
refundTimeout = 30

def kafkaCon(topic, key):
    consumer = KafkaConsumer(topic, bootstrap_servers=[kafka_server], auto_offset_reset='earliest')
    for message in consumer:
        if message.key.decode('UTF-8') == key:
            return pickle.loads(message.value)['data']
    return None

#
# Auxiliar functions
#
def is_valid_queryparam(param):
    return param != '' and param is not None

def getTotalAmount(payment_id):
    refunds = Refund.objects.filter(payment_id=payment_id)
    amount = 0
    for refund in refunds:
        amount += refund.amount
    return amount

def refundTimePassed(initial_date):
    global refundTimeout
    date_now = datetime.datetime.now()
    delta = datetime.timedelta(minutes=refundTimeout)
    return date_now-delta > initial_date

def filter(request):
    refunds = Refund.objects.all()
    refund_id = request.GET.get('refund_id')
    payment_id = request.GET.get('payment_id')

    if is_valid_queryparam(refund_id) and refund_id != "Choose...":
        refunds = refunds.filter(refund_id=refund_id)
    
    if is_valid_queryparam(payment_id) and payment_id != "Choose...":
        refunds = refunds.filter(payment_id=payment_id)

    return refunds

def paymentToString(payment):
    return 'Payment ID: ' + str(payment['payment_id']) + ", Amount: " + str(payment['amount']) + "€, Method: " + payment['payment_method'] + ", Status: " + payment['status'] + ", Created at: " + payment['created_at'].strftime("%Y-%m-%d %H:%M:%S") + "\n" 

#
# Views that return Responses
#
def listAllRefunds(request):
    allRefunds = []
    for r in Refund.objects.all():
        refundDict = model_to_dict(r)
        refundDict['created_at'] = r.created_at
        allRefunds.append(refundDict)
    return JsonResponse({'refunds': allRefunds})

@csrf_exempt
def setRefundTimeout(request):
    global refundTimeout
    t = request.POST.get('timeout')
    if is_valid_queryparam(t):
        refundTimeout = t
        return HttpResponse('Refund timeout successfully set to ' + str(refundTimeout))
    return HttpResponseBadRequest('Invalid parameter input')

@csrf_exempt
def newRefund(request, payment_id):
    global refundTimeout
    start_date = datetime.datetime.now()
    refundAmount = float(request.POST.get('refund_amount'))
    payment = kafkaCon(topic='payment', key=payment_id)
    if payment != None:
        totalPaid = getTotalAmount(payment_id)
        remaining_amount = payment['amount']-totalPaid
        if remaining_amount > 0:
            if refundTimePassed(start_date):
                return HttpResponseServerError('Could not process refund on time.')
            else:
                refundAmount = float(request.POST.get('refund_amount'))
                if refundAmount > remaining_amount:
                    refund = Refund()
                    refund.payment_id = payment_id
                    refund.amount = refundAmount
                    return HttpResponseBadRequest('Refund amount must be less than or equal to ' + float(remaining_amount))  
                else:
                    return HttpResponse('New refund created.')
        else:
            return HttpResponse('Payment with ID ' + str(payment_id) + " has been fully refunded.")

def showRefund(request, refund_id):
    refund = get_object_or_404(Refund, refund_id=refund_id)
    payment = kafkaCon(topic='payment', key=refund.payment_id)
    if payment != None:
        refundDict = model_to_dict(refund)
        refundDict['created_at'] = refund.created_at
        return JsonResponse({'refund': refundDict, 'payment': payment})      
    return HttpResponseServerError("Could not access payments service!")

def filterRefunds(request):
    refunds= [model_to_dict(r) for r in filter(request)]
    return JsonResponse({'filteredRefunds': refunds})

#
# Views that render a GUI
#
def listAllRefundsGUI(request):
    global refundTimeout
    allRefunds = Refund.objects.all()
    t = request.GET.get('timeout')
    if is_valid_queryparam(t):
        refundTimeout = t
    return render(request, 'refunds/allRefunds.html', {'allRefunds': allRefunds, 'payments_url': payments_url, 'refundTimeout': refundTimeout})

def newRefundGUI(request, payment_id):
    global refundTimeout
    start_date = datetime.datetime.now()
    payment = kafkaCon(topic='payment', key=payment_id)

    if payment != None:
        totalPaid = getTotalAmount(payment_id)
        remaining_amount = payment['amount']-totalPaid
        if remaining_amount > 0:
            form = RefundForm(request.POST or None)
            if form.is_valid() and not refundTimePassed(start_date):
                if float(form['amount'].value()) > remaining_amount:
                    messages.info(request, 'Cannot create a new refund with that amount. Max amount is: ' + str(remaining_amount))
                    return render(request, 'refunds/createRefund.html', {'form': form, 'payment_id': payment_id, 'remaining_amount': remaining_amount})  
                form.save()
                return redirect(payments_url+'payment/'+payment_id)
            return render(request, 'refunds/createRefund.html', {'form': form, 'payment_id': payment_id, 'remaining_amount': remaining_amount})
        else:
            return HttpResponse('Payment with ID ' + str(payment_id) + " has been fully refunded.")

def filterRefundsGUI(request):
    all_refund_ids = list(Refund.objects.all().values_list('refund_id', flat=True))
    all_payment_ids = list(Refund.objects.all().values_list('payment_id', flat=True).distinct())
    return render(request, 'refunds/filterRefunds.html', {'refunds': filter(request), 'refund_ids': all_refund_ids, 'payment_ids': all_payment_ids})

def showRefundGUI(request, refund_id):
    refund = get_object_or_404(Refund, refund_id=refund_id)
    payment = kafkaCon(topic='payment', key=refund.payment_id)
    if payment != None:
        return render(request, 'refunds/showRefund.html', {'refund_id': refund_id, 'refund': refund, 'payment': paymentToString(payment)})      
    return HttpResponseServerError("Could not access payments service!")