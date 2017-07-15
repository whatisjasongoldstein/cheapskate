import datetime
from django.test import TestCase

from ..models import (Account, Charge, Withdrawal, Deposit,
    IncomeCategory, ExpenseCategory, CCBill)

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

    def setUp(self):
        self.account, _ = Account.objects.get_or_create(title="CC", kind="cc")
        self.category, _ = ExpenseCategory.objects.get_or_create(title="Things")
        
        self.bill = CCBill.objects.create(
            amount=500,
            account=self.account,
        )

        self.charge1 = Charge.objects.create(
            title="Charge1",
            amount=100,
            account=self.account,
            category=self.category,
        )

        self.charge2 = Charge.objects.create(
            title="Charge2",
            amount=200,
            account=self.account,
            category=self.category,
        )

        self.charge3 = Charge.objects.create(
            title="Charge3",
            amount=300,
            account=self.account,
            category=self.category,
        )

    def test_is_paid_when_false(self):
        self.bill.charges.add(self.charge1)
        self.assertFalse(self.bill.is_paid)

    def test_is_paid_when_true(self):
        self.charge1.paid = True
        self.charge1.save()
        self.bill.charges.add(self.charge1)
        self.assertTrue(self.bill.is_paid)
    
    def test_total_charges_empty(self):
        self.assertEqual(self.bill.total_charges(), 0)

    def test_total_charges_filled(self):
        self.bill.charges.add(self.charge1)
        self.assertEqual(self.bill.total_charges(), 100)
    
    def test_balances_exact(self):
        self.bill.charges.add(self.charge2)
        self.bill.charges.add(self.charge3)
        self.assertEqual(self.bill.balances(), "Exact")
        
    def test_balances_over(self):
        self.bill.charges.add(self.charge1)
        self.bill.charges.add(self.charge2)
        self.bill.charges.add(self.charge3)
        self.assertEqual(self.bill.balances(), "$100.00 over")

    def test_balances_over(self):
        self.bill.charges.add(self.charge1)
        self.bill.charges.add(self.charge3)
        self.assertEqual(self.bill.balances(), "$100.00 short")
    
    def test_get_create_url(self):
        url = CCBill.get_create_url()
        expected = "/credit-card-bills/add/"
        self.assertEqual(url, expected)
    
    def test_get_absolute_url(self):
        expected = "/credit-card-bills/%s/" % self.bill.id
        url = self.bill.get_absolute_url()
        self.assertEqual(url, expected)


class DepositTests(TestCase):
    def setUp(self):
        self.account, _ = Account.objects.get_or_create(title="Acc", kind="checking")
        self.category, _ = IncomeCategory.objects.get_or_create(title="Things")
        self.deposit = Deposit.objects.create(
            title="Paycheck",
            amount=10,  # ouch!
            category=self.category,
            account=self.account,
        )

    def test_get_absolute_url(self):
        expected = "/deposits/%s/" % self.deposit.id
        url = self.deposit.get_absolute_url()
        self.assertEqual(url, expected)

    def test_get_create_url(self):
        expected = "/deposits/add/"
        url = Deposit.get_create_url()
        self.assertEqual(url, expected)

    def test_search_by_title(self):
        result = Deposit.search("pay")
        self.assertEqual(result[0], self.deposit)

    def test_search_by_amount(self):
        # As a string
        result = Deposit.search("10")
        self.assertEqual(result[0], self.deposit)

        # As an int
        result = Deposit.search(10)
        self.assertEqual(result[0], self.deposit)

        # As a decimal
        result = Deposit.search("10.00")
        self.assertEqual(result[0], self.deposit)

    def test_search_miss(self):
        result = Deposit.search("Nothing")
        self.assertEqual(len(result), 0)


class WithdrawalTests(TestCase):
    def setUp(self):
        self.account, _ = Account.objects.get_or_create(title="Acc", kind="checking")
        self.category, _ = ExpenseCategory.objects.get_or_create(title="Things")
        self.rent = Withdrawal.objects.create(
            title="Rent",
            amount=200,  # Wishful thinking
            category=self.category,
            account=self.account,
        )

    def test_get_absolute_url(self):
        expected = "/withdrawals/%s/" % self.rent.id
        url = self.rent.get_absolute_url()
        self.assertEqual(url, expected)

    def test_get_create_url(self):
        expected = "/withdrawals/add/"
        url = Withdrawal.get_create_url()
        self.assertEqual(url, expected)

    def test_search_by_title(self):
        result = Withdrawal.search("rent")
        self.assertEqual(result[0], self.rent)

    def test_search_by_amount(self):
        # As a string
        result = Withdrawal.search("200")
        self.assertEqual(result[0], self.rent)

        # As an int
        result = Withdrawal.search(200)
        self.assertEqual(result[0], self.rent)

        # As a decimal
        result = Withdrawal.search("200.00")
        self.assertEqual(result[0], self.rent)

    def test_search_miss(self):
        result = Withdrawal.search("Nothing")
        self.assertEqual(len(result), 0)
