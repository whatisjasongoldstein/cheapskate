import datetime
from django.test import TestCase

from ..models import (Account, Charge, Withdrawal, Deposit,
    IncomeCategory, ExpenseCategory)

class ExpenseCategoryTests(TestCase):

    def setUp(self):
        self.category, _ = ExpenseCategory.objects.get_or_create(title="Foo")
        self.cc, _ = Account.objects.get_or_create(title="CC", kind="cc")
        self.bank, _ = Account.objects.get_or_create(title="CC", kind="checking")

    def test_total(self):
        """
        Test ExpenseCategory.total for the current month.
        """        
        Charge.objects.create(
            title="Charge1",
            amount=10,
            category=self.category,
            account=self.cc,
        )
        Charge.objects.create(
            title="Charge2",
            amount=10,
            category=self.category,
            account=self.cc,
        )

        Withdrawal.objects.create(
            title="Withdrawal 1",
            amount=10,
            category=self.category,
            account=self.bank,
        )

        # Should not be included
        Charge.objects.create(
            title="OldCharge",
            amount=200,
            date=datetime.date(2015, 1, 1),
            category=self.category,
            account=self.cc,
        )
        self.assertEqual(self.category.total(), 30)

    def test_total_with_specified_date(self):
        """
        Test ExpenseCategory.total for an explicit month.
        """        
        Charge.objects.create(
            title="Charge1",
            amount=50,
            date=datetime.date(2017, 1, 2),
            category=self.category,
            account=self.cc,
        )

        Withdrawal.objects.create(
            title="Withdrawal 1",
            amount=50,
            date=datetime.date(2017, 1, 15),
            category=self.category,
            account=self.bank,
        )
        result = self.category.total(month=1, year=2017)
        self.assertEqual(result, 100)


class IncomeCategoryTests(TestCase):

    def setUp(self):
        self.category, _ = IncomeCategory.objects.get_or_create(title="Paycheck")
        self.bank, _ = Account.objects.get_or_create(title="CC", kind="checking")

    def test_total(self):
        """
        Test IncomeCategory.total for the current month.
        """
        for i in range(0, 3):
            Deposit.objects.create(
                title="Deposit %s" % i,
                amount=100,
                account=self.bank,
                category=self.category,
            )
        result = self.category.total()
        self.assertEqual(result, 300)

    def test_total_with_specified_date(self):
        """
        Test IncomeCategory.total for given month.
        """
        for i in range(0, 3):
            Deposit.objects.create(
                title="Deposit %s" % i,
                amount=100,
                account=self.bank,
                category=self.category,
                date=datetime.date(2017, 7, i + 1),
            )

        # Should not be included
        Deposit.objects.create(
            title="Deposit %s" % i,
            amount=100,
            account=self.bank,
            category=self.category,
            date=datetime.date(2017, 6, 15),
        )

        result = self.category.total(month=7, year=2017)
        self.assertEqual(result, 300)


class ChargeTests(TestCase):
   
    def setUp(self):
        self.cc, _ = Account.objects.get_or_create(title="CC", kind="cc")
        self.category, _ = ExpenseCategory.objects.get_or_create(title="Things")
        self.coffee_charge = Charge.objects.create(
            title="Coffee",
            amount=2,
            account=self.cc,
            category=self.category,
        )

    def test_str(self):
        self.assertEqual(str(self.coffee_charge), "Coffee for $2")

    def test_get_absolute_url(self):
        url = self.coffee_charge.get_absolute_url()
        expected = "/charges/%s/" % self.coffee_charge.id
        self.assertEqual(url, expected)

    def test_get_create_url(self):
        expected = "/charges/add/"
        url = Charge.get_create_url()
        self.assertEqual(url, expected)

    def test_search_by_title(self):
        result = Charge.search("coffee")
        self.assertEqual(result[0], self.coffee_charge)

    def test_search_by_amount(self):
        # As a string
        result = Charge.search("2")
        self.assertEqual(result[0], self.coffee_charge)

        # As an int
        result = Charge.search(2)
        self.assertEqual(result[0], self.coffee_charge)

        # As a decimal
        result = Charge.search("2.00")
        self.assertEqual(result[0], self.coffee_charge)

    def test_search_miss(self):
        result = Charge.search("Nothing")
        self.assertEqual(len(result), 0)


class CCBillTests(TestCase):
    def is_paid(self):
        pass
    
    def total_charges(self):
        pass
    
    def balances(self):
        pass
    
    def get_create_url(self):
        pass
    
    def get_absolute_url(self):
        pass


class DepositTests(TestCase):
    pass

class WithdrawalTests(TestCase):
    pass
