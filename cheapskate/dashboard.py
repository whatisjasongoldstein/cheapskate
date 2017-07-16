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

    @cached_property
    def total_recurring_amounts(self):
        # Use common events from past months to predict
        # future months.
        kwargs = {
            "date__year": self.year,
            "date__month__in": [m.index for m in self.past_months],
            "do_not_project": False,
            "category__isnull": False, 
        }

        # All common events
        charges = Charge.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        withdrawals = Withdrawal.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        expenses = charges + withdrawals;

        income = Deposit.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

        return {
            "income": income,
            "expenses": expenses,
        }

    @cached_property
    def total_one_off_amounts(self):
        # Some entries, such as trips or big purchases, aren't
        # good predictors of future months.

        # One-off events
        kwargs = {
            "date__year": self.year,
            "do_not_project": True,
            "category__isnull": False, 
        }
        charges = Charge.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        withdrawals = Withdrawal.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

        expenses = charges + withdrawals
        income = Deposit.objects.filter(**kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

        return {
            "income": income,
            "expenses": expenses,
        }

    @cached_property
    def projected(self):
        num_months = len(self.past_months)
        
        # Don't make assumptions if no months have elapsed.
        if not num_months:
            return {
                "income": 0,
                "expenses": 0,
                "net": 0,
            }

        income = self.total_recurring_amounts["income"]
        expenses = self.total_recurring_amounts["expenses"]
        one_off_income = self.total_one_off_amounts["income"]
        one_off_expenses = self.total_one_off_amounts["expenses"]

        # Add the one-offs to the projected totals based
        # on common events.
        projected_income = (income / num_months * 12) + one_off_income
        projected_expenses = (expenses / num_months * 12) + one_off_expenses
        projected_net = projected_income - projected_expenses

        data = {
            "income": projected_income,
            "expenses": projected_expenses,
            "net": projected_net,
        }
        if data["income"]:
            data["percent"] = int(round((data["net"] / data["income"]) * 100))
        return data



