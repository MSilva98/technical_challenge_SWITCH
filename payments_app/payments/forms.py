from django import forms
from django.forms import widgets

class SettleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        pay_id = kwargs.pop('payment_id')
        amt = kwargs.pop('amount')
        sttl_at = kwargs.pop('settle_date')
        sttl_amt = kwargs.pop('settled_amount')
        super(SettleForm, self).__init__(*args, **kwargs)        
        self.fields['payment_id'] = forms.CharField(widget=widgets.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), initial=pay_id, disabled=True)
        self.fields['amount'] = forms.FloatField(widget=widgets.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), disabled=True, initial=amt)                
        self.fields['settled_at'] = forms.DateTimeField(widget=widgets.TextInput(attrs={'class': 'form-control', 'type': 'date'}),required=True, initial=sttl_at) 
        self.fields['settled_amount'] = forms.FloatField(widget=widgets.NumberInput(attrs={'class': 'form-control'}),required=True, max_value=amt, min_value=sttl_amt, initial=sttl_amt)

class FilterForm(forms.Form):
    filter_choices = (
        ('payment_id', 'PAYMENT_ID'),
        ('amount', 'AMOUNT'),
        ('payment_method', 'PAYMENT_METHOD'),
        ('status', 'STATUS'),
        ('created_at', 'CREATED_AT'),
        ('settled_at', 'SETTLED_AT'),
    )
    search = forms.CharField(required=False)
    filter_field = forms.ChoiceField(choices=filter_choices)