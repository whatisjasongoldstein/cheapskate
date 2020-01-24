from __future__ import absolute_import

from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe

from .widgets import JSONSelectMultiple
from .models import (Account, Charge, Withdrawal, Deposit,
    ExpenseCategory, IncomeCategory, CCBill)


class DefaultAccountMixin(object):

    def __init__(self, *args, **kwargs):
        super(DefaultAccountMixin, self).__init__(*args, **kwargs)
        if self.fields["account"].queryset.count() > 0:
            self.initial["account"] = self.fields["account"].queryset[0]

        self.fields["category"].queryset = self.fields["category"].queryset.filter(
            Q(archived=False) | Q(id=getattr(self.instance, "category_id"))
        )


class ChargeForm(DefaultAccountMixin, forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Charge
        exclude = []


class WithdrawalForm(DefaultAccountMixin, forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Withdrawal
        exclude = []


class DepositForm(DefaultAccountMixin, forms.ModelForm):

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
            charges_qs = Charge.objects.filter(
                Q(id__in=current_charges) | Q(paid=False)
            ).select_related("category")
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
