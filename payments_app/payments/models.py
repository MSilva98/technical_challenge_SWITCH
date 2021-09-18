from django import forms
from django.db import models
from django.forms import ModelForm
import uuid

class Base(models.Model):
    CC = "credit_card"
    MBWay = "mbway"
    
    SUCCESS = "success"
    ERROR = "error"
    SETTLED = "settled"

    pay_method = (
        (CC, 'credit_card'),
        (MBWay, 'mbway')
    )
    statusOP = (
        (SUCCESS, 'success'),
        (ERROR, 'error'),
        (SETTLED, 'settled')
    )

    payment_id = models.UUIDField(max_length=200, primary_key=True, default=uuid.uuid4)     # primary key, auto generated UUID
    amount = models.FloatField()                
    payment_method = models.CharField(max_length=50, default=CC, choices=pay_method)
    created_at = models.DateTimeField(auto_now_add=True)          
    status = models.CharField(max_length=20, choices=statusOP)
    settled_at = models.DateTimeField(null=True, blank=True)             
    settled_amount = models.FloatField(null=True, blank=True, default=0)
    def __str__(self):
        baseStr = "Payment ID: " + str(self.payment_id) + ", Amount: " + str(self.amount) + "€, Method: " + self.payment_method + ", Created at: " + str(self.created_at) + ", Status: " + self.status 
        if self.settled_at != None:
            return baseStr + ", Settled at: " + str(self.settled_at) + ", Settled amount: " + str(self.settled_amount) + "€"
        else:
            return baseStr

class CreditCard(models.Model):
    payment_id = models.OneToOneField(Base, on_delete=models.CASCADE)  # Foreign key to Base
    number = models.CharField(max_length=16)                                     
    name = models.CharField(max_length=30)                             
    expiration_month = models.CharField(max_length=2)   
    expiration_year = models.CharField(max_length=4)  
    cvv = models.CharField(max_length=3)
    def __str__(self):
        return str(self.payment_id) + ", Card Number: " + self.number + ", Name: " + self.name + ", Exp. Month: " + self.expiration_month + ", Exp. Year: " + self.expiration_year + ", CVV: " + self.cvv + "\n"
        
class MbWay(models.Model):
    payment_id = models.OneToOneField(Base, on_delete=models.CASCADE)  # Foreign key to base
    phone_number = models.CharField(max_length=9)
    def __str__(self):
        return str(self.payment_id) + ", Phone Number: " + self.phone_number + "\n"

class BaseForm(ModelForm):
    class Meta:
        model = Base
        fields = ('payment_id', 'amount', 'payment_method', 'status', 'settled_at', 'settled_amount')
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}, choices=Base.pay_method),
            'settled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
            'settled_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'default': 0}),
            'status': forms.HiddenInput(attrs={'class': 'form-control', 'default': Base.ERROR}),
        }

class CreditCardForm(ModelForm):
    class Meta:
        model = CreditCard
        fields = '__all__'
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1111111111111111, 'placeholder': 1111111111111111}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'expiration_month': forms.NumberInput(attrs={'class': 'form-control', 'max': 12, 'min': 1}),
            'expiration_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2021}),
            'cvv': forms.NumberInput(attrs={'class': 'form-control', 'max': 999}),
        }

class MbWayForm(ModelForm):
    class Meta:
        model = MbWay
        fields = '__all__'
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control', 'maxlength': 9, 'placeholder': 910000000})
        }
