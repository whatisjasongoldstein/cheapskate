from django.test import TestCase, Client
from django.contrib.auth.models import User

from cheapskate.models import Charge, Deposit, Withdrawal, CCBill
from cheapskate.forms import ChargeForm, CCBillForm, WithdrawalForm, DepositForm

class ChargeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'myuser', 'myemail@test.com', "password", is_staff=True)
        self.client = Client()
        self.client.login(username='myuser', password='password')
        self.add_resp = self.client.get('/charges/add/')

    def test_add_charge_loads(self):
        self.assertEqual(self.add_resp.status_code, 200)

    def test_add_charge_template(self):
        self.assertEqual(self.add_resp.templates[0].name, "form.html")

    def test_add_charge_context(self):
        context = self.add_resp.context
        self.assertIsInstance(context["form"], ChargeForm)
        self.assertIsInstance(context["instance"], Charge)
        self.assertEqual(context["title"], "Create Charge")

    def test_post(self):
        pass  # TODO


class DepositViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'myuser', 'myemail@test.com', "password", is_staff=True)
        self.client = Client()
        self.client.login(username='myuser', password='password')
        self.add_resp = self.client.get('/charges/add/')

    def test_add_charge_loads(self):
        self.assertEqual(self.add_resp.status_code, 200)

    def test_add_charge_template(self):
        self.assertEqual(self.add_resp.templates[0].name, "form.html")

    def test_add_charge_context(self):
        context = self.add_resp.context
        self.assertIsInstance(context["form"], ChargeForm)
        self.assertIsInstance(context["instance"], Charge)
        self.assertEqual(context["title"], "Create Charge")

    def test_post(self):
        pass  # TODO

class WithdrawalViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'myuser', 'myemail@test.com', "password", is_staff=True)
        self.client = Client()
        self.client.login(username='myuser', password='password')
        self.add_resp = self.client.get('/withdrawals/add/')

    def test_add_charge_loads(self):
        self.assertEqual(self.add_resp.status_code, 200)

    def test_add_charge_template(self):
        self.assertEqual(self.add_resp.templates[0].name, "form.html")

    def test_add_charge_context(self):
        context = self.add_resp.context
        self.assertIsInstance(context["form"], WithdrawalForm)
        self.assertIsInstance(context["instance"], Withdrawal)
        self.assertEqual(context["title"], "Create Withdrawal")

    def test_post(self):
        pass  # TODO


class CCBillViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'myuser', 'myemail@test.com', "password", is_staff=True)
        self.client = Client()
        self.client.login(username='myuser', password='password')
        self.add_resp = self.client.get('/credit-card-bills/add/')

    def test_add_charge_loads(self):
        self.assertEqual(self.add_resp.status_code, 200)

    def test_add_charge_template(self):
        self.assertEqual(self.add_resp.templates[0].name, "form.html")

    def test_add_charge_context(self):
        context = self.add_resp.context
        self.assertIsInstance(context["form"], CCBillForm)
        self.assertIsInstance(context["instance"], CCBill)
        self.assertEqual(context["title"], "Create Credit Card Bill")

    def test_post(self):
        pass  # TODO
