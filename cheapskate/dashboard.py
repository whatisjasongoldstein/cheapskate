from __future__ import absolute_import

import json
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
            "expenses": round(sum_expense(date__year=self.year, date__month=self.index), 2),
            "income": round(sum_income(date__year=self.year, date__month=self.index), 2),
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
                "total": round(category.total(month=self.index, year=self.year), 2)
            })

        self.income_categories = []
        for category in _income_categories:
            self.income_categories.append({
                "title": category.title,
                "total": round(category.total(month=self.index, year=self.year), 2)
            })
        


class Dashboard(object):

    def __init__(self, year=None):
        today = datetime.date.today()

        try:
            year = int(year)
        except TypeError:
            year = None
        self.year = year or today.year

        self.months = [Month(i, self.year) for i in xrange(1, 13)]

        self.past_months = self.months
        if self.year == today.year:
            self.past_months = [m for m in self.months if m.index < today.month]

    @cached_property
    def ytd(self):
        data = {
            "income": sum([m.totals["income"] for m in self.past_months]),
            "expenses": sum([m.totals["expenses"] for m in self.past_months]),
            "net": sum([m.totals["net"] for m in self.past_months]),
        }
        if data["income"]:
            data["percent"] = int(round((data["net"] / data["income"]) * 100))
        return data

    @cached_property
    def projected(self):
        num_months = len(self.past_months)
        if not num_months:
            return {
                "income": 0,
                "expenses": 0,
                "net": 0,
            }

        data = {
            "income": sum([m.totals["income"] for m in self.past_months]) / num_months * 12,
            "expenses": sum([m.totals["expenses"] for m in self.past_months]) / num_months * 12,
            "net": sum([m.totals["net"] for m in self.past_months]) / num_months * 12,
        }
        if data["income"]:
            data["percent"] = int(round((data["net"] / data["income"]) * 100))
        return data        

    @cached_property
    def chart_json_data(self):
        data = {
            "expenses": [],
            "income": [], 
            "net": [],
            "percent": [],
        }
        today = datetime.date.today()
        for month in self.months[0:today.month]:
            data["expenses"].append(month.totals["expenses"])
            data["income"].append(month.totals["income"])
            data["net"].append(month.totals["net"])
            if "percent" in month.totals:
                data["percent"].append(month.totals["percent"])
        return data
