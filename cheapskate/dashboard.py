from __future__ import absolute_import

from functools import lru_cache

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

def get_expenses(month, year, category=None, one_off=None):
    kwargs = {
        "date__year": year,
        "category__isnull": False,
    }

    if month is not None:
        kwargs["date__month"] = month

    if category:
        kwargs["category"] = category

    if one_off is not None:
        kwargs["is_one_off"] = one_off

    return sum_amounts(Charge, kwargs) + sum_amounts(Withdrawal, kwargs)


def get_incomes(month, year, category=None, one_off=None):
    kwargs = {
        "date__year": year,
        "category__isnull": False,
    }

    if month is not None:
        kwargs[ "date__month"] = month

    if category:
        kwargs["category"] = category

    if one_off is not None:
        kwargs["is_one_off"] = one_off

    return sum_amounts(Deposit, kwargs)


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
                "total": get_expenses(index, year, category=category)
            })

        self.income_categories = []
        for category in _income_categories:
            self.income_categories.append({
                "title": category.title,
                "total": get_incomes(index, year, category=category)
            })


PAST = "past"
ONE_OFF = "one_off"


def get_expense_categories(year):
    cats = []
    qs = ExpenseCategory.objects.all().order_by("title")
    for cat in qs:
        if get_expenses(None, year, category=cat) > 0:
            cats.append(cat)
    return cats


def get_income_categories(year):
    cats = []
    qs = IncomeCategory.objects.all().order_by("title")
    for cat in qs:
        if get_incomes(None, year, category=cat) > 0:
            cats.append(cat)
    return cats



class Dashboard(object):

    def __init__(self, year=None):
        try:
            year = int(year)
        except TypeError:
            year = None
        self.year = year or self.today.year

        # Make this query here once and pass it around.
        expense_categories = get_expense_categories(self.year)
        income_categories = get_income_categories(self.year)

        # Categories should be in the order of how
        # expensive they are
        expense_categories = sorted(expense_categories,
            key=lambda cat: get_expenses(None, self.year, category=cat),
            reverse=True)

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
        elif self.year < self.today.year:
            return self.months
        return []

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
                "is_one_off": False,
                "category__isnull": False,
            },
            ONE_OFF: {
                "date__year": self.year,
                "is_one_off": True,
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

        # If there are past months
        # we can't take an average.
        if not self.past_months:
            return 0
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

        # If there are past months
        # we can't take an average.
        if not self.past_months:
            return 0
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

    @cached_property
    def for_chart(self):
        data = {
            "incomes": [],
            "incomes_normal": [],
            "incomes_one_off": [],
            "expenses": [],
            "expenses_normal": [],
            "expenses_one_off": [],
        }

        for m in self.months:
            data["incomes"].append(get_incomes(m.index, m.year))
            data["incomes_normal"].append(get_incomes(m.index, m.year, one_off=False))
            data["incomes_one_off"].append(get_incomes(m.index, m.year, one_off=True))

            data["expenses"].append(get_expenses(m.index, m.year))
            data["expenses_normal"].append(get_expenses(m.index, m.year, one_off=False))
            data["expenses_one_off"].append(get_expenses(m.index, m.year, one_off=True))
        return data

