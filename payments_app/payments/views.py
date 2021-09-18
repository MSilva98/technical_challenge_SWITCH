from django.forms.models import model_to_dict
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Base, CreditCard, MbWay, BaseForm, CreditCardForm, MbWayForm
from kafka import KafkaProducer
import pickle

from django.views.decorators.csrf import csrf_exempt
import datetime

# Refunds microservice url (only used in GUI version to redirect to newRefund page)
refunds_url = 'http://172.26.1.2:2222/api/refunds/'

# Kafka URL
kafka_server = 'kafka:9092'

def kafkaProd(topic, key, data):
    producer = KafkaProducer(bootstrap_servers=kafka_server)
    serialized_data = pickle.dumps({'data': data}, pickle.HIGHEST_PROTOCOL)
    try:
        producer.send(topic, key=bytes(key,'utf-8'), value=serialized_data)
        producer.flush()
        return True
    except AssertionError:
        return False

#
# Auxiliar functions
#
def is_date(str):
    try:
        datetime.datetime.strptime(str, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

def findPayment(payment_id):
    payment = get_object_or_404(Base, payment_id=payment_id)    
    # credit_card
    if payment.payment_method == Base.CC:   
        full_payment = CreditCard.objects.get(payment_id=payment_id)
    # MBWay
    else:                                   
        full_payment = MbWay.objects.get(payment_id=payment_id)
    return payment, full_payment

def is_valid_queryparam(param):
    return param != '' and param is not None

def filter(request):
    payments = Base.objects.all()
    payment_id = request.GET.get('payment_id')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    payment_method = request.GET.get('payment_method')
    status = request.GET.get('status')
    min_created_at = request.GET.get('min_created_at')
    max_created_at = request.GET.get('max_created_at')
    min_settled_at = request.GET.get('min_settled_at')
    max_settled_at = request.GET.get('max_settled_at')

    if is_valid_queryparam(payment_id) and payment_id != "Choose...":
        payments = payments.filter(payment_id=payment_id)

    if is_valid_queryparam(min_amount):
        payments = payments.filter(amount__gte=min_amount)

    if is_valid_queryparam(max_amount):
        payments = payments.filter(amount__lte=max_amount)

    if is_valid_queryparam(payment_method) and payment_method != "Choose...":
        payments = payments.filter(payment_method=payment_method)

    if is_valid_queryparam(status) and status != "Choose...":
        payments = payments.filter(status=status)

    if is_valid_queryparam(min_created_at):
        payments = payments.filter(created_at__gte=min_created_at)

    if is_valid_queryparam(max_created_at):
        payments = payments.filter(created_at__lt=max_created_at)

    if is_valid_queryparam(min_settled_at):
        payments = payments.filter(settled_at__gte=min_settled_at)

    if is_valid_queryparam(max_settled_at):
        payments = payments.filter(settled_at__lt=max_settled_at)

    return payments

def settlePayment_aux(payment_id):
    payment = get_object_or_404(Base, payment_id=payment_id)
    amount = payment.amount
    payment.settled_amount = amount
    payment.settled_at = datetime.datetime.now()
    payment.status = Base.SETTLED
    payment.save()

#
# Views that return Responses
# 
def listAllPayments(request):
    allPayments = []
    for p in Base.objects.all():
        refundDict = model_to_dict(p)
        refundDict['created_at'] = p.created_at
        allPayments.append(refundDict)
    return JsonResponse({'payments': allPayments}, status=200)

def showPayment(request, payment_id):
    payment, fullPayment = findPayment(payment_id)
    if payment == None:
        return HttpResponseNotFound('Payment not found')
    paymentDict = model_to_dict(payment)
    paymentDict['created_at'] = payment.created_at
    paymentDict['additional_parameters'] = model_to_dict(fullPayment)
    return JsonResponse({'base': paymentDict}, status=200)

def filterPayments(request):
    payments = [model_to_dict(p) for p in filter(request)]
    return JsonResponse({'filteredPayments': payments}, status=200)

@csrf_exempt
def newPayment(request):
    if request.method == 'POST':
        payment = Base()
        payment.amount = request.POST.get('amount')
        payment.payment_method = request.POST.get('payment_method')
        if 'settled_at' in request.POST:
            settled_at = request.POST.get('settled_at')
            if not is_date(settled_at):
                return HttpResponseBadRequest('"settled_at must have a format YYYY-MM-DD HH:MM"')
            else:
                payment.settled_at = request.POST.get('settled_at')
                payment.settled_amount = request.POST.get('settled_amount')
        payment.status = Base.SUCCESS
        if payment.settled_amount == payment.amount:
            payment.status = Base.SETTLED
        if payment.payment_method == Base.CC:
            cc = CreditCard()
            cc.payment_id = payment
            cc.number = request.POST.get('number')
            cc.name = request.POST.get('name')
            cc.expiration_month = request.POST.get('expiration_month')
            cc.expiration_year = request.POST.get('expiration_year')
            cc.cvv = request.POST.get('cvv')
            payment.save()
            cc.save()
        elif payment.payment_method == Base.MBWay:
            mbway = MbWay()
            mbway.payment_id = payment
            mbway.phone_number = request.POST.get('phone_number')
            payment.save()
            mbway.save()
        else:
            payment.status = Base.ERROR
            payment.save()
            return HttpResponseBadRequest('Bad payment method')
        
        paymentDict = model_to_dict(payment)
        paymentDict['created_at'] = payment.created_at
        if kafkaProd(topic='payment', key=str(payment.payment_id), data=paymentDict):
            return HttpResponse('New payment created.',status=200)
        else:
            payment.delete()
            return HttpResponse('Payment could not be published to topic.', status=503)
    return HttpResponseBadRequest("Data not found.")        

def settlePayment(request, payment_id):
    settlePayment_aux(payment_id)
    return HttpResponse('Payment settled.', status=200)

def deletePayment(request, payment_id):
    get_object_or_404(Base, payment_id=payment_id).delete()
    return HttpResponse('Payment ' + payment_id + ' deleted.', status=200)

#
# Views that render a GUI
#
def listAllPaymentsGUI(request):
    allPayments = Base.objects.all()
    return render(request, 'payments/allPayments.html', {'allPayments': allPayments})

def showPaymentGUI(request, payment_id):
    payment, full_payment = findPayment(payment_id)
    context = {
        'payment_id': payment_id, 
        'payment': full_payment, 
        'notSettled': payment.amount!=payment.settled_amount, 
        'refunds_url': refunds_url
    }
    return render(request, 'payments/showPayment.html', context)

def filterPaymentsGUI(request):
    return render(request, 'payments/filterPayments.html', {'payments': filter(request), 'payment_ids': list(Base.objects.all().values_list('payment_id', flat=True)), 'status': Base.statusOP, 'pay_method': Base.pay_method})

def newPaymentGUI(request):
    form = BaseForm(request.POST or None)
    payment_id = form['payment_id'].value()
    if form.is_valid():
        form.save()
        request.session['payment_id'] = payment_id
        request.session['payment_method'] = form['payment_method'].value()
        return redirect('payments:processPayment')
    return render(request, 'payments/createPayment.html', {'form': form})

def processPayment(request):
    payment_method = request.session['payment_method']
    payment_id = request.session['payment_id']
    basePayment = get_object_or_404(Base, payment_id=payment_id)
    # Only one payment method can be associated with a payment
    if not CreditCard.objects.filter(payment_id=payment_id) and not MbWay.objects.filter(payment_id=payment_id):
        if payment_method == Base.CC:
            form = CreditCardForm(request.POST or None, initial={'payment_id': payment_id})
        else:
            form = MbWayForm(request.POST or None, initial={'payment_id': payment_id})
        if form.is_valid():
            form.save()
            if float(basePayment.amount) == float(basePayment.settled_amount):
                basePayment.status = Base.SETTLED
            else:
                basePayment.status = Base.SUCCESS
            basePayment.save()
            paymentDict = model_to_dict(basePayment)
            paymentDict['created_at'] = basePayment.created_at
            kafkaProd(topic='payment', key=payment_id, data=paymentDict)
            return redirect('payments:allPaymentsGUI')
        return render(request, 'payments/processPayment.html', {'form': form, 'payment_method': payment_method})
    return HttpResponse("Only one payment method can be associated to a payment.")

def settlePaymentGUI(request, payment_id):
    settlePayment_aux(payment_id) 
    return redirect('payments:showPaymentGUI', payment_id)

def deletePaymentGUI(request, payment_id):
    get_object_or_404(Base, payment_id=payment_id).delete()
    return redirect('payments:allPaymentsGUI')