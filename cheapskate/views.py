from __future__ import absolute_import

import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.fields import Field

from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from django.template.defaultfilters import slugify
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from django.utils.functional import cached_property

from .models import (Charge, CCBill, ExpenseCategory, IncomeCategory, Deposit, Withdrawal)
from .dashboard import Dashboard
from .forms import ChargeForm, DepositForm, WithdrawalForm, CCBillForm
from .helpers import add_url_parameter


from django.utils.decorators import method_decorator


class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(*args, **kwargs)


@staff_member_required
def index(request):
    dashboard = Dashboard(year=request.GET.get("year"))
    years = range(datetime.date.today().year, Charge.objects.filter(date__isnull=False).first().date.year - 1, -1)
    return render(request, "index.html", 
        {
            "dashboard": dashboard,
            "years": years,
        })


class ListBaseView(StaffRequiredMixin, View):
    model = None
    template = "list.html"
    row_template = None
    filter_by = []

    @cached_property
    def create_url(self):
        return self.model.get_create_url()

    @cached_property
    def search_term(self):
        return self.request.GET.get("search", None)

    @cached_property
    def queryset_filters(self):
        """
        For any get parameters that match the filter_by
        list, pass the key/values straight into the ORM.

        The ORM handles escaping, so the worst thing that
        happens is the whole rule gets ignored.
        """
        filters = {}
        get_params_items = self.request.GET.items()
        for key, value in get_params_items:
            bare_key = key.split("_")[0]
            if bare_key not in self.filter_by or value == "":
                continue
            filters[key] = value
        return filters

    @cached_property
    def queryset(self):
        if self.search_term and hasattr(self.model, "search"):
            return self.model.search(self.search_term).select_related()
        
        related_fields = [r for r in ("category", "account") if hasattr(self.model, r)]
        return (self.model.objects.filter(**self.queryset_filters)
                    .select_related(*related_fields)
                    .order_by("-date"))

    @cached_property
    def previous_page_url(self):
        if self.page.has_previous():
            return add_url_parameter(self.request.get_full_path(), "page", self.page.previous_page_number())
        return None

    @cached_property
    def next_page_url(self):
        if self.page.has_next():
            return add_url_parameter(self.request.get_full_path(), "page", self.page.next_page_number())
        return None

    @cached_property
    def page(self):
        paginator = Paginator(self.queryset, 100)
        page = paginator.page(self.request.GET.get("page", 1))
        return page

    @cached_property
    def catergory_choices(self):
        if hasattr(self.model, "category"):
            return self.model.category.get_queryset()
        return None

    @cached_property
    def object_list(self):
        return self.page.object_list

    def get(self, *args, **kwargs):
        return render(self.request, self.template, {
            "object_list": self.object_list,
            "row_template": self.row_template,
            "page": self.page,
            "next_page_url": self.next_page_url,
            "previous_page_url": self.previous_page_url,
            "search_term": self.search_term,
            "title": str(self.model._meta.verbose_name_plural.title()),
            "create_url": self.create_url,
            "filter_by": self.filter_by,
            "filters": self.queryset_filters,
            "categories": self.catergory_choices,
        })


class ObjectBaseView(StaffRequiredMixin, View):
    model = None
    template = "form.html"
    form_cls = None
    back_url = "../"

    @cached_property
    def title(self):
        if self.instance.id:
            return str(self.instance)
        return "Create %s" % self.model._meta.verbose_name.title()

    @cached_property
    def instance(self):
        if "id" in self.kwargs:
            return get_object_or_404(self.model, id=self.kwargs["id"])
        return self.model()

    @cached_property
    def form(self):
        return self.form_cls(self.request.POST or None, self.request.FILES or None, instance=self.instance)

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


class ChargeListView(ListBaseView):
    model = Charge
    row_template = "rows/charge-row.html"
    filter_by = ["category", "date", "paid"]


class ChargeView(ObjectBaseView):
    model = Charge
    form_cls = ChargeForm


class DepositListView(ListBaseView):
    model = Deposit
    row_template = "rows/deposit-row.html"
    filter_by = ["category", "date"]


class DepositView(ObjectBaseView):
    model = Deposit
    form_cls = DepositForm


class WithdrawalListView(ListBaseView):
    model = Withdrawal
    row_template = "rows/withdrawal-row.html"
    filter_by = ["category", "date"]


class WithdrawalView(ObjectBaseView):
    model = Withdrawal
    form_cls = WithdrawalForm


class CCBillListView(ListBaseView):
    model = CCBill
    row_template = "rows/cc-bill-row.html"

    def post(self, *args, **kwargs):
        bill_pk = self.request.POST.get("markpaid", None)
        if bill_pk:
            Charge.objects.filter(ccbill__id=bill_pk).update(paid=True)
            messages.add_message(self.request, messages.SUCCESS, "All charges marked as paid.")
        return self.get(*args, **kwargs)


class CCBillView(ObjectBaseView):
    model = CCBill
    form_cls = CCBillForm

    @cached_property
    def post_save_redirect(self):
        if self.request.POST.get("save_and_create"):
            return self.model.get_create_url()
        return self.instance.get_absolute_url()


@staff_member_required
def income_category(request, slug):
    year = request.GET.get('year') or datetime.date.today().year

    rough_cats = IncomeCategory.objects.all().values('title', 'id')
    cat_dict = {}
    for r in rough_cats:
        cat_dict[slugify(r['title'])] = r['id']

    cat_id = cat_dict.get(slug)
    if not cat_id:
        raise Http404
    category = IncomeCategory.objects.get(id=cat_id)
    objs = category.deposit_set.filter(date__year=year)
    total = sum([obj.amount for obj in objs])

    return render(request, "category.html", {
            'objs': objs,
            'category': category,
            'year': year,
            'total': total,
        })


@staff_member_required
def expense_category(request, slug):
    year = request.GET.get('year') or datetime.date.today().year

    rough_cats = ExpenseCategory.objects.all().values('title', 'id')
    cat_dict = {}
    for r in rough_cats:
        cat_dict[slugify(r['title'])] = r['id']

    cat_id = cat_dict.get(slug)
    if not cat_id:
        raise Http404
    category = ExpenseCategory.objects.get(id=cat_id)
    objs = list(category.charge_set.filter(date__year=year)) + list(category.withdrawal_set.filter(date__year=year))
    objs = sorted(objs, key=lambda obj: obj.date)

    total = sum([obj.amount for obj in objs])

    return render(request, "category.html", {
            'objs': objs,
            'category': category,
            'year': year,
            'total': total,
        })
