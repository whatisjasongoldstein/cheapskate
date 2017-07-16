import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User

from cheapskate.views.dashboard_views import index

class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'myuser', 'myemail@test.com', "password", is_staff=True)
        self.client = Client()
        self.client.login(username='myuser', password='password')
        self.resp = self.client.get('/')

    def test_dashboard_loads(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_correct_template(self):
        self.assertEqual(self.resp.templates[0].name, "index.html")

    def test_correct_context(self):
        context = self.resp.context
        self.assertIn("dashboard", context)
        self.assertIn("years", context)

    def test_default_year(self):
        expected = datetime.date.today().year
        actual = self.resp.context["dashboard"].year
        self.assertEqual(actual, expected)

    def test_specified_year(self):
        resp = self.client.get('/?year=2015')
        self.assertEqual(resp.context["dashboard"].year, 2015)

