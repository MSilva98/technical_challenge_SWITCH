from django import forms
from django.db import models
from django.forms import ModelForm
import uuid

from django.forms.widgets import HiddenInput, Widget

# Create your models here.

class Base(models.Model):
    CC = "credit_card"
    MBWay = "mbway"
    SUCCESS = "success"
    ERROR = "error"
    SETTLED = "settled"

    payment_id = models.UUIDField(max_length=200, primary_key=True, default=uuid.uuid4)     # primary key, auto generated UUID
    amount = models.FloatField()                
    payment_method = models.CharField(max_length=50, default=CC, choices=[(CC, 'credit_card'), (MBWay, 'mbway')])
    created_at = models.DateTimeField(auto_now_add=True)          
    status = models.CharField(max_length=20, choices=[(SUCCESS, 'success'), (ERROR, 'error'), (SETTLED, 'settled')])
    settled_at = models.DateTimeField(null=True)             
    settled_amount = models.FloatField(null=True)
    def __str__(self):
        baseStr = "Payment ID: " + str(self.payment_id) + ", Amount: " + str(self.amount) + "€, Method: " + self.payment_method + ", Created at: " + str(self.created_at) + ", Status: " + self.status 
        if self.settled_at != None:
            return baseStr + ", Settled at: " + str(self.settled_at) + ", Settled amount: " + str(self.settled_amount) + "€"
        else:
            return baseStr

class CreditCard(models.Model):
    payment_id = models.ForeignKey(Base, on_delete=models.CASCADE)  # Foreign key to Base
    number = models.CharField(max_length=16)                                     
    name = models.CharField(max_length=30)                             
    expiration_month = models.CharField(max_length=2)   
    expiration_year = models.CharField(max_length=4)  
    cvv = models.CharField(max_length=3)
    def __str__(self):
        return str(self.payment_id) + ", Card Number: " + self.number + ", Name: " + self.name + ", Exp. Month: " + self.expiration_month + ", Exp. Year: " + self.expiration_year + ", CVV: " + self.cvv + "\n"
        
class MbWay(models.Model):
    payment_id = models.ForeignKey(Base, on_delete=models.CASCADE)  # Foreign key to base
    phone_number = models.CharField(max_length=9)
    def __str__(self):
        return str(self.payment_id) + ", Phone Number: " + self.phone_number + "\n"

class BaseForm(ModelForm):
    settled_at = forms.DateTimeField(required=False)
    settled_amount = forms.FloatField(required=False)
    status = forms.CharField(widget=HiddenInput(), required=False, initial=Base.ERROR)
    class Meta:
        model = Base
        fields = ('payment_id', 'amount', 'payment_method', 'status', 'settled_at', 'settled_amount')
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    # This save only happens when Success
    # def save(self, commit=True):
    #     base = super().save(commit=False)
    #     base.status = Base.SUCCESS
    #     base.save(commit=commit)
    #     return base

class CreditCardForm(ModelForm):
    class Meta:
        model = CreditCard
        fields = '__all__'
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }

class MbWayForm(ModelForm):
    class Meta:
        model = MbWay
        fields = '__all__'
        widgets = {
            'payment_id': forms.TextInput(attrs={'readonly': 'readonly'})
        }
