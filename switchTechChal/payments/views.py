from django import forms
from django.db.models import base
from django.db.models.base import Model
from django.http.response import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template import loader

from .models import Base, CreditCard, MbWay, BaseForm, CreditCardForm, MbWayForm
from .forms import SettleForm

# Create your views here.
def listAll(request):
    allPayments = Base.objects.all()
    return render(request, 'payments/allPayments.html', {'allPayments': allPayments})

def showPayment(request, payment_id):
    payment = get_object_or_404(Base, payment_id=payment_id)    
    # credit_card
    if payment.payment_method == Base.CC:   
        full_payment = CreditCard.objects.get(payment_id=payment_id)
    # MBWay
    else:                                   
        full_payment = MbWay.objects.get(payment_id=payment_id)
    return render(request, 'payments/showPayment.html', {'payment_id': payment_id, 'payment': full_payment, 'notSettled': payment.amount!=payment.settled_amount})

def searchByPaymentId(request, payment_id):
    allPayments = Base.objects.filter(payment_id=payment_id)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'payment_id', 'payment_id': payment_id})

def searchByAmount(request, min_amount=None, max_amount=None):
    allPayments = Base.objects.filter(amount__lte=max_amount, amount__gte=min_amount)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'amount', 'min': min_amount, 'max': max_amount})

def searchByMethod(request, method):
    allPayments = Base.objects.filter(payment_method=method)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'payment_method', 'method': method})

def searchByStatus(request, status):
    allPayments = Base.objects.filter(status=status)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'status', 'status': status})

def searchByCreation(request, min_created=None, max_created=None):
    allPayments = Base.objects.filter(created_at__lte=max_created, created_at__gte=min_created)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'creation_date', 'min': min_created, 'max': max_created})

def searchBySettlement(request, min_settle=None, max_settle=None):
    allPayments = Base.objects.filter(settled_amount__lte=max_settle, settled_amount__gte=min_settle)
    return render(request, 'payments/filteredPayments.html', {'allPayments': allPayments, 'filter': 'settled_amount', 'min': min_settle, 'max': max_settle})

def newPayment(request):
    form = BaseForm(request.POST or None)
    payment_id = form['payment_id'].value()
    if form.is_valid():
        form.save()
        payment_method = form['payment_method'].value()
        request.session['payment_id'] = payment_id
        request.session['payment_method'] = payment_method
        return redirect('payments:processPayment')
    return render(request, 'payments/createPayment.html', {'payment_id': payment_id, 'form': form})

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
    return render(request, 'payments/processPayment.html', {'form': form})

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
            payment.save()
            return redirect('payments:showPayment', payment_id)
    return render(request, 'payments/settlePayment.html', {'payment_id': payment_id, 'form': form})

def deletePayment(request, payment_id):
    get_object_or_404(Base, payment_id=payment_id).delete()
    return redirect('payments:allPayments')

