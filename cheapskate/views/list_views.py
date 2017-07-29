from django.contrib import messages
from django.shortcuts import render
from django.views.generic import View
from django.utils.functional import cached_property
from django.core.paginator import Paginator

from ..helpers import add_url_parameter
from ..models import Charge, Deposit, Withdrawal, CCBill

from .mixins import StaffRequiredMixin


class ListBaseView(StaffRequiredMixin, View):
    model = None
    template = "list.html"
    row_template = None
    filter_by = []
    title = "List of Things TK"

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
    def pagination_urls(self):
        """
        Next and previous pages
        """
        result = {"next": None, "preview": None}
        path = self.request.get_full_path()

        if self.page.has_previous():
            num = self.page.previous_page_number()
            result["previous"] = add_url_parameter(path, "page", num)

        if self.page.has_next():
            num = self.page.next_page_number()
            result["next"] = add_url_parameter(path, "page", num)

        return result

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
            "pagination_urls": self.pagination_urls,
            "search_term": self.search_term,
            "title": self.title,
            "create_url": self.create_url,
            "filter_by": self.filter_by,
            "filters": self.queryset_filters,
            "categories": self.catergory_choices,
        })


class ChargeListView(ListBaseView):
    model = Charge
    title = "Charges"
    row_template = "rows/charge-row.html"
    filter_by = ["category", "date", "paid"]


class DepositListView(ListBaseView):
    model = Deposit
    title = "Deposits"
    row_template = "rows/deposit-row.html"
    filter_by = ["category", "date"]


class WithdrawalListView(ListBaseView):
    model = Withdrawal
    title = "Withdrawals"
    row_template = "rows/withdrawal-row.html"
    filter_by = ["category", "date"]


class CCBillListView(ListBaseView):
    model = CCBill
    title = "Credit Card Bills"
    row_template = "rows/cc-bill-row.html"

    def post(self, *args, **kwargs):
        bill_pk = self.request.POST.get("markpaid", None)
        if bill_pk:
            Charge.objects.filter(ccbill__id=bill_pk).update(paid=True)
            messages.add_message(self.request, messages.SUCCESS, 
                "All charges marked as paid.")
        return self.get(*args, **kwargs)
