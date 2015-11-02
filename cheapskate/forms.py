from __future__ import absolute_import

from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe

from .widgets import JSONSelectMultiple
from .models import (Account, Charge, Withdrawal, Deposit, 
    ExpenseCategory, IncomeCategory, CCBill)


class ChargeForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Charge
        exclude = []


class WithdrawalForm(forms.ModelForm):
    
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Withdrawal
        exclude = []


class DepositForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Deposit
        exclude = []


class CCBillForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    
    def __init__(self, *args, **kwargs):
        super(CCBillForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            current_charges = list(self.instance.charges.values_list("pk", flat=True))
            charges_qs = Charge.objects.filter(Q(id__in=current_charges) | Q(paid=False))
            self.fields["charges"].widget = JSONSelectMultiple(
                attrs={"data-credit-card-charge-filter": 1}, 
                choices=[(obj.id, {
                    "id": obj.id,
                    "title": obj.title,
                    "date": obj.date.isoformat(),
                    "amount": obj.amount,
                    "category": obj.category.title,
                    "url": obj.get_absolute_url(),
                }) for obj in charges_qs])
        else:
            self.fields.pop("charges", None)

    class Meta:
        model = CCBill
        exclude = []
