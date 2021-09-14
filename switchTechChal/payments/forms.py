from django import forms

class SettleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        pay_id = kwargs.pop('payment_id')
        amt = kwargs.pop('amount')
        sttl_at = kwargs.pop('settle_date')
        sttl_amt = kwargs.pop('settled_amount')
        super(SettleForm, self).__init__(*args, **kwargs)        
        self.fields['payment_id'] = forms.CharField(max_length=200, initial=pay_id, disabled=True)     # primary key, auto generated UUID
        self.fields['amount'] = forms.FloatField(disabled=True, initial=amt)                
        self.fields['settled_at'] = forms.DateTimeField(required=False, initial=sttl_at) 
        self.fields['settled_amount'] = forms.FloatField(required=False, max_value=amt, min_value=sttl_amt, initial=sttl_amt)