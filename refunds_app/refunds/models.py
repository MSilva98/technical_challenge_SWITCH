from django import forms
from django.db import models
from django.forms.models import ModelForm
import uuid


class Refund(models.Model):
    refund_id = models.UUIDField(max_length=200, primary_key=True, default=uuid.uuid4)
    payment_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    def __str__(self):
        return "Refund ID:" + str(self.refund_id) + ", Payment ID: " + str(self.payment_id) + ", Created at: " + str(self.created_at) + ", Amount: " + str(self.amount) + "€\n" 

class RefundForm(ModelForm):
    class Meta:
        model = Refund
        fields = '__all__'
        widgets = {
            'refund_id': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'payment_id': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 0}),
        }