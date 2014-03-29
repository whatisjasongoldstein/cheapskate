from __future__ import absolute_import

import calendar
import datetime

from django.utils.functional import cached_property

from .models import Charge, Withdrawal, ExpenseCategory, IncomeCategory, Deposit


def sum_amounts(cls, kwargs):
    return sum(cls.objects.filter(**kwargs).values_list("amount", flat=True))

def sum_income(**kwargs):
    kwargs["category__isnull"] = False
    return sum_amounts(Deposit, kwargs)

def sum_expense(**kwargs):
    withdrawal_kwargs = kwargs.copy()
    withdrawal_kwargs["category__isnull"] = False
    return sum_amounts(Withdrawal, withdrawal_kwargs) + sum_amounts(Charge, kwargs)


class Month(object):
    
    def __init__(self, index, year):
        self.index = index
        self.year = year
        self.name = calendar.month_name[self.index]
        
        self.totals = {
            "expenses": sum_expense(date__year=self.year, date__month=self.index),
            "income": sum_income(date__year=self.year, date__month=self.index),
        }
        self.totals["net"] = self.totals["income"] - self.totals["expenses"]
        if self.totals["income"]:
            self.totals["percent"] = int(round((self.totals["net"] / self.totals["income"]) * 100))

        _expense_categories = ExpenseCategory.objects.all().order_by("title")
        _income_categories = IncomeCategory.objects.all().order_by("title")

        self.expense_categories = []
        for category in _expense_categories:
            self.expense_categories.append({
                "title": category.title,
                "total": category.total(month=self.index, year=self.year)
            })

        self.income_categories = []
        for category in _income_categories:
            self.income_categories.append({
                "title": category.title,
                "total": category.total(month=self.index, year=self.year)
            })
        


class Dashboard(object):

    def __init__(self, year=None):
        today = datetime.date.today()
        self.year = int(year or today.year)
        self.months = [Month(i, self.year) for i in xrange(1, 13)]

        self.ytd = {
            "income": sum([m.totals["income"] for m in self.months]),
            "expenses": sum([m.totals["expenses"] for m in self.months]),
            "net": sum([m.totals["net"] for m in self.months]),
        }
        if self.ytd["income"]:
            self.ytd["percent"] = int(round((self.ytd["net"] / self.ytd["income"]) * 100))

        past_months =  [m for m in self.months if m.index < today.month]
        num_months = len(past_months)
        self.projected = {
            "income": sum([m.totals["income"] for m in self.months]) / num_months * 12,
            "expenses": sum([m.totals["expenses"] for m in self.months]) / num_months * 12,
            "net": sum([m.totals["net"] for m in self.months]) / num_months * 12,
        }
        if self.projected["income"]:
            self.projected["percent"] = int(round((self.projected["net"] / self.projected["income"]) * 100))


