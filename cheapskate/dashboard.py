from __future__ import absolute_import

import calendar
import datetime

from django.db import models
from django.utils.functional import cached_property

from .models import Charge, Withdrawal, ExpenseCategory, IncomeCategory, Deposit


def sum_amounts(cls, kwargs):
    data = cls.objects.filter(**kwargs).aggregate(models.Sum("amount"))
    return (data["amount__sum"] or 0)  # If QS is empty, this would be None

def sum_income(**kwargs):
    kwargs["category__isnull"] = False
    return sum_amounts(Deposit, kwargs)

def sum_expense(**kwargs):
    withdrawal_kwargs = kwargs.copy()
    withdrawal_kwargs["category__isnull"] = False
    return sum_amounts(Withdrawal, withdrawal_kwargs) + sum_amounts(Charge, kwargs)


class Month(object):
    
    def __init__(self, index, year, expense_categories=None, income_categories=None):
        self.index = index
        self.year = year
        self.name = calendar.month_name[self.index]
        _expense_categories = expense_categories or []
        _income_categories = income_categories or []
        
        self.totals = {
            "expenses": sum_expense(date__year=self.year, date__month=self.index),
            "income": sum_income(date__year=self.year, date__month=self.index),
        }
        self.totals["net"] = self.totals["income"] - self.totals["expenses"]
        if self.totals["income"]:
            self.totals["percent"] = int(round((
                self.totals["net"] / self.totals["income"]) * 100))

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

PAST = "past"
ONE_OFF = "one_off"


class Dashboard(object):

    def __init__(self, year=None):
        try:
            year = int(year)
        except TypeError:
            year = None
        self.year = year or self.today.year

        # Make this query here once and pass it around.
        expense_categories = list(ExpenseCategory.objects.all().order_by("title"))
        income_categories = list(IncomeCategory.objects.all().order_by("title"))

        self.months = [Month(i, self.year,
            expense_categories=expense_categories,
            income_categories=income_categories) for i in range(1, 13)]

    @property
    def today(self):
        """
        Mockable way to get today's date.
        """
        return datetime.date.today()

    @cached_property
    def past_months(self):
        if self.year == self.today.year:
            return [m for m in self.months if m.index < self.today.month]
        return self.months

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

    @property
    def filters(self):
        """
        Params for filtering all records.
        """
        return {
            PAST: {
                "date__year": self.year,
                "date__month__in": [m.index for m in self.past_months],
                "do_not_project": False,
                "category__isnull": False, 
            },
            ONE_OFF: {
                "date__year": self.year,
                "do_not_project": True,
                "category__isnull": False, 
            }
        }

    @cached_property
    def average_monthly_income(self):
        """
        Excluding one off events.
        """
        income = Deposit.objects.filter(**self.filters[PAST]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        return (income / len(self.past_months))

    @cached_property
    def average_monthly_expenses(self):
        """
        Excluding one off events.
        """
        charges = Charge.objects.filter(**self.filters[PAST]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        withdrawals = Withdrawal.objects.filter(**self.filters[PAST]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        return ((charges + withdrawals) / len(self.past_months))

    @cached_property
    def one_off_income(self):
        return Deposit.objects.filter(**self.filters[ONE_OFF]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

    @cached_property
    def one_off_expenses(self):
        charges = Charge.objects.filter(**self.filters[ONE_OFF]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        withdrawals = Withdrawal.objects.filter(**self.filters[ONE_OFF]
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        return (charges + withdrawals)

    @cached_property
    def projected(self):
        # Don't make assumptions if no months have elapsed.
        if not len(self.past_months):
            return {
                "income": 0,
                "expenses": 0,
                "net": 0,
            }

        # Add the one-offs to the projected totals based
        # on common events.
        projected_income = ((self.average_monthly_income * 12) + 
                             self.one_off_income)
        projected_expenses = ((self.average_monthly_expenses * 12) + 
                             self.one_off_expenses)
        projected_net = projected_income - projected_expenses

        data = {
            "income": projected_income,
            "expenses": projected_expenses,
            "net": projected_net,
        }
        if data["income"]:
            data["percent"] = int(round((data["net"] / data["income"]) * 100))
        return data



