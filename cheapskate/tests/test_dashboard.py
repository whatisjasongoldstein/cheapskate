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
    
    def test_basic_month(self):
        """
        Default properties, no data.
        """
        month = Month(1, 2017)
        self.assertEqual(month.expense_categories, [])
        self.assertEqual(month.income_categories, [])
        self.assertEqual(month.index, 1)
        self.assertEqual(month.name, "January")
        self.assertEqual(month.totals, {
            "expenses": 0,
            "income": 0,
            "net": 0,
        })

class DashboardTests(TestCase):
    pass