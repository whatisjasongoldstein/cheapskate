from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.utils.functional import cached_property
from django.contrib import messages

from .mixins import StaffRequiredMixin
from ..models import Charge, Deposit, Withdrawal, CCBill
from ..forms import ChargeForm, DepositForm, WithdrawalForm, CCBillForm


class ObjectBaseView(StaffRequiredMixin, View):
    model = None
    template = "form.html"
    form_cls = None
    back_url = "../"

    @property
    def object_title(self):
        return self.model._meta.verbose_name.title()

    @cached_property
    def title(self):
        if self.instance.id:
            return str(self.instance)
        return "Create %s" % self.object_title

    @cached_property
    def instance(self):
        if "id" in self.kwargs:
            return get_object_or_404(self.model, id=self.kwargs["id"])
        return self.model()

    @cached_property
    def form(self):
        return self.form_cls(self.request.POST or None,
                             self.request.FILES or None,
                             instance=self.instance)

    @cached_property
    def post_save_redirect(self):
        if self.request.POST.get("save_and_create"):
            return self.model.get_create_url()
        return self.request.POST.get("next", "../")

    @cached_property
    def context(self):
        return {
            "form": self.form,
            "instance": self.instance,
            "title": self.title,
        }

    def get(self, *args, **kwargs):
        return render(self.request, self.template, self.context)

    def post(self, *args, **kwargs):
        if self.form.is_valid():
            if self.request.POST.get("delete", False):
                self.instance.delete()
            else:
                self.form.save()
            messages.add_message(self.request, messages.SUCCESS, "Done! That was easy.")
            return HttpResponseRedirect(self.post_save_redirect)
        messages.add_message(self.request, messages.ERROR, "Please fix your shit.")
        return self.get(*args, **kwargs)


class ChargeView(ObjectBaseView):
    model = Charge
    form_cls = ChargeForm


class DepositView(ObjectBaseView):
    model = Deposit
    form_cls = DepositForm


class WithdrawalView(ObjectBaseView):
    model = Withdrawal
    form_cls = WithdrawalForm


class CCBillView(ObjectBaseView):
    model = CCBill
    form_cls = CCBillForm

    @cached_property
    def post_save_redirect(self):
        if self.request.POST.get("save_and_create"):
            return self.model.get_create_url()
        return self.instance.get_absolute_url()

