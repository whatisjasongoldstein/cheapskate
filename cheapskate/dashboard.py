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
            self.totals["percent"] = int(round((self.totals["net"] / self.totals["income"]) * 100))

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

        try:
            year = int(year)
        except TypeError:
            year = None
        self.year = year or today.year

        # Make this query here once and pass it around.
        expense_categories = list(ExpenseCategory.objects.all().order_by("title"))
        income_categories = list(IncomeCategory.objects.all().order_by("title"))

        self.months = [Month(i, self.year,
            expense_categories=expense_categories,
            income_categories=income_categories) for i in xrange(1, 13)]

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
        
        # Don't make assumptions if no months have elapsed.
        if not num_months:
            return {
                "income": 0,
                "expenses": 0,
                "net": 0,
            }

        # Some entries, such as trips or big purchases, aren't
        # good predictors of future months.
        

        # Use common events from past months to predict
        # future months.
        recurring_kwargs = {
            "date__year": self.year,
            "date__month__in": [m.index for m in self.past_months],
            "do_not_project": False,
            "category__isnull": False, 
        }

        # All common events
        charges = Charge.objects.filter(**recurring_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        withdrawals = Withdrawal.objects.filter(**recurring_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        expenses = charges + withdrawals;

        income = Deposit.objects.filter(**recurring_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

        # One-off events
        one_of_kwargs = {
            "date__year": self.year,
            "do_not_project": True,
            "category__isnull": False, 
        }
        one_off_charges = Charge.objects.filter(**one_of_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0
        one_off_withdrawals = Withdrawal.objects.filter(**one_of_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

        one_off_expenses = one_off_charges + one_off_withdrawals
        one_off_income = Deposit.objects.filter(**one_of_kwargs
            ).aggregate(models.Sum("amount"))["amount__sum"] or 0

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



