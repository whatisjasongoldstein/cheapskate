import datetime
from django.test import TestCase

from ..dashboard import (Month, Dashboard,
    sum_amounts, sum_expense, sum_income)
from ..models import (Charge, Withdrawal, Deposit,
    ExpenseCategory, IncomeCategory, Account)


class DashboardHelpersTests(TestCase):

    def setUp(self):
        self.exp_category1, _ = ExpenseCategory.objects.get_or_create(title="Foo")
        self.exp_category2, _ = ExpenseCategory.objects.get_or_create(title="Bar")

        self.inc_category1, _ = IncomeCategory.objects.get_or_create(title="Paycheck")
        self.inc_category2, _ = IncomeCategory.objects.get_or_create(title="Etc")

        self.cc, _ = Account.objects.get_or_create(title="CC", kind="cc")
        self.bank, _ = Account.objects.get_or_create(title="CC", kind="checking")

        Charge.objects.create(
            title="Charge1",
            amount=10,
            category=self.exp_category1,
            account=self.cc,
        )

        Charge.objects.create(
            title="Charge2",
            amount=10,
            category=self.exp_category1,
            account=self.cc,
        )

        Charge.objects.create(
            title="Charge Other Category",
            amount=1000,
            category=self.exp_category2,
            account=self.cc,
        )

        Withdrawal.objects.create(
            title="Withdrawal 1",
            amount=40,
            category=self.exp_category1,
            account=self.bank,
        )

        # These should be ignored
        Withdrawal.objects.create(
            title="Withdrawal Null",
            amount=7777,
            category=None,
            account=self.bank,
        )

        Deposit.objects.create(
            title="Deposit 1",
            amount=100,
            account=self.bank,
            category=self.inc_category1,
        )

        Deposit.objects.create(
            title="Deposit 2",
            amount=100,
            account=self.bank,
            category=self.inc_category2,
        )

        # These should be ignored
        Deposit.objects.create(
            title="Deposit Null",
            amount=4,
            account=self.bank,
            category=None,
        )

    def test_sum_amounts(self):
        """
        Add the amounts of objects by a class
        and kwargs, such as filtering
        charges by category.
        """
        result = sum_amounts(Charge, {
            "category": self.exp_category1,
        })
        self.assertEqual(result, 20)

        result = sum_amounts(Charge, {
            "category": self.exp_category2,
        })
        self.assertEqual(result, 1000)

    def test_sum_income_unfiltered(self):
        result = sum_income()
        self.assertEqual(result, 200)

    def test_sum_income_with_category_filter(self):
        result = sum_income(**{
            "category": self.inc_category1,
        })
        self.assertEqual(result, 100)

    def test_sum_expense_unfiltered(self):
        result = sum_expense()
        self.assertEqual(result, 1060)

    def test_sum_expense_filtered_by_category(self):
        result = sum_expense(**{
            "category": self.exp_category1,
        })
        self.assertEqual(result, 60)


class MonthTests(TestCase):

    def setUp(self):
        self.exp_category, _ = ExpenseCategory.objects.get_or_create(title="Foo")
        self.inc_category, _ = IncomeCategory.objects.get_or_create(title="Bar")

        self.cc, _ = Account.objects.get_or_create(title="CC", kind="cc")
        self.bank, _ = Account.objects.get_or_create(title="CC", kind="checking")

        # Test charges for months will be in Feb. 2017
        Charge.objects.create(
            title="Charge1",
            amount=100,
            date=datetime.date(2017, 2, 2),
            category=self.exp_category,
            account=self.cc,
        )

        Charge.objects.create(
            title="Charge2",
            amount=25,
            date=datetime.date(2017, 2, 25),
            category=self.exp_category,
            account=self.cc,
        )

        Charge.objects.create(
            title="Some other time",
            amount=1000,
            date=datetime.date(2017, 1, 1),
            category=self.exp_category,
            account=self.cc,
        )

        Deposit.objects.create(
            title="Deposit 1",
            amount=500,
            date=datetime.date(2017, 2, 19),
            account=self.bank,
            category=self.inc_category,
        )

        # Create two months
        self.empty_month = Month(1, 2015,
            income_categories=[self.inc_category],
            expense_categories=[self.exp_category])
        self.full_month = Month(2, 2017,
            income_categories=[self.inc_category],
            expense_categories=[self.exp_category])

    def test_empty_month_totals(self):
        """
        Should all be zero
        """
        self.assertEqual(self.empty_month.totals, {
            "expenses": 0,
            "income": 0,
            "net": 0,
        })

    def test_empty_month_categories_totals(self):
        """
        Should be all zero.
        """
        self.assertEqual(self.empty_month.expense_categories, [
            {"title": self.exp_category.title, "total": 0},
        ])

        self.assertEqual(self.empty_month.income_categories, [
            {"title": self.inc_category.title, "total": 0},
        ])

    def test_month_names(self):
        """
        Pulled from calendar by their index.
        """
        self.assertEqual(self.empty_month.name, "January")
        self.assertEqual(self.full_month.name, "February")

    def test_full_month_totals(self):
        """
        Should add up records from the 
        given month.
        """
        self.assertEqual(self.full_month.totals, {
            'expenses': 125.0,
            'income': 500.0,
            'net': 375.0,
            'percent': 75,
        })

    def test_month_category_totals(self):
        """
        Records should be totaled and avaialble
        as a list of categories.
        """
        self.assertEqual(self.full_month.expense_categories, [
            {"title": self.exp_category.title, "total": 125.0},
        ])

        self.assertEqual(self.full_month.income_categories, [
            {"title": self.inc_category.title, "total": 500.0},
        ])



class DashboardTests(TestCase):
    pass

