from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import requests

from .models import Base, CreditCard, MbWay, BaseForm, CreditCardForm, MbWayForm
from .forms import SettleForm

# Refunds microservice url
refunds_url = 'http://172.26.1.2:2222/api/refunds/'

def listAllPayments(request):
    allPayments = Base.objects.all()
    return render(request, 'payments/allPayments.html', {'allPayments': allPayments})

def getAllPaymentsID(request):
    allPaymentsID = [payment_id for payment_id in Base.objects.values_list('payment_id', flat=True)]
    return JsonResponse({'paymentsID': allPaymentsID})

def getAllPayments(request):
    allPayments = [model_to_dict(payment) for payment in Base.objects.all()]
    return JsonResponse({'payments': allPayments})

def findPayment(payment_id):
    payment = get_object_or_404(Base, payment_id=payment_id)    
    # credit_card
    if payment.payment_method == Base.CC:   
        full_payment = CreditCard.objects.get(payment_id=payment_id)
    # MBWay
    else:                                   
        full_payment = MbWay.objects.get(payment_id=payment_id)
    return payment, full_payment

def getPayment(request, payment_id):
    payment, _ = findPayment(payment_id)
    paymentDict = model_to_dict(payment)
    paymentDict['created_at'] = payment.created_at
    return JsonResponse(paymentDict)

def showPayment(request, payment_id):
    r = requests.get(refunds_url+'refundedAmount/'+payment_id)
    if r.status_code == 200:
        data = r.json()
    payment, full_payment = findPayment(payment_id)
    context = {
        'payment_id': payment_id, 
        'payment': full_payment, 
        'notSettled': payment.amount!=payment.settled_amount, 
        'fullyRefunded': payment.amount==data['refunded_amount'], 
        'refunds_url': refunds_url
    }
    return render(request, 'payments/showPayment.html', context)

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

def filterView(request):
    return render(request, 'payments/filterPayments.html', {'payments': filter(request), 'payment_ids': list(Base.objects.all().values_list('payment_id', flat=True)), 'status': Base.statusOP, 'pay_method': Base.pay_method})

def newPayment(request):
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
        return redirect('payments:allPayments')
    return render(request, 'payments/processPayment.html', {'form': form, 'payment_method': payment_method})

def settlePayment(request, payment_id):
    payment = get_object_or_404(Base, payment_id=payment_id)
    amount = payment.amount
    settled_amount = payment.settled_amount
    last_settle = payment.settled_at
    if amount > settled_amount:
        form = SettleForm(request.POST or None, payment_id=payment_id, amount=amount, settle_date=last_settle, settled_amount=settled_amount)
        if form.is_valid():
            amt = float(form['settled_amount'].value())
            payment.settled_amount = amt
            payment.settled_at = form['settled_at'].value()
            if amt == amount:
                payment.status = Base.SETTLED
            else:
                payment.status = Base.SUCCESS
            payment.save()
            return redirect('payments:showPayment', payment_id)
    return render(request, 'payments/settlePayment.html', {'payment_id': payment_id, 'form': form})

def deletePayment(request, payment_id):
    get_object_or_404(Base, payment_id=payment_id).delete()
    return redirect('payments:allPayments')

