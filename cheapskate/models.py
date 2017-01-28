from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
import datetime

ACCOUNT_CHOICES = (
    ('checking', 'Checking'),
    ('cc', 'Credit Card')
)


class Account(models.Model):
    """ A checking or credit card account """
    title = models.CharField(max_length=255)
    bank = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=ACCOUNT_CHOICES)

    def __unicode__(self):
        return self.title


class ExpenseCategory(models.Model):
    title = models.CharField(max_length=150)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"

    def total(self, month=datetime.date.today().month, year=datetime.date.today().year):
        """ Returns the total expenses for the category in a given month. """
        result = sum(
                Charge.objects.filter(category__id=self.id, 
                    date__year=year, date__month=month).values_list('amount', flat=True)
            ) + sum(
                Withdrawal.objects.filter(category__id=self.id, 
                    date__year=year, date__month=month).values_list('amount', flat=True)
            )
        return result


class IncomeCategory(models.Model):
    title = models.CharField(max_length=150)

    def __unicode__(self):
        return self.title

    def total(self, month=datetime.date.today().month, year=datetime.date.today().year):
        """ Returns the totali income for the category in a given month."""
        return sum(Deposit.objects.filter(
                    category_id=self.id, 
                    date__year=year, 
                    date__month=month
                    ).values_list('amount', flat=True))


class Charge(models.Model):
    """ A credit card change. """
    title = models.CharField(max_length=250)
    amount = models.FloatField()
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ExpenseCategory)
    paid = models.BooleanField(default=False)
    lost = models.BooleanField(default=False)
    account = models.ForeignKey(Account, limit_choices_to={'kind':'cc'})
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    do_not_project = models.BooleanField("One-off Event", default=False)

    def __unicode__(self):
        try:
            text = (u"%s for $%s") % (self.title, self.amount)
        except Exception as e:
            import debug
        return text

    def get_absolute_url(self):
        return reverse("edit_charge", kwargs={"id": self.id})

    @classmethod
    def get_create_url(cls):
        return reverse("add_charge")

    @classmethod
    def search(cls, term):
        # kwargs
        query = Q(title__icontains=term) | Q(notes__icontains=term)
        try:
            num_term = float(term)
            query = query | Q(amount=num_term)
        except ValueError:
            pass
        return cls.objects.filter(query).order_by("-date")


class CCBill(models.Model):
    """ A credit card bill. """
    amount = models.FloatField()
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    charges = models.ManyToManyField('Charge', blank=True)
    account = models.ForeignKey(Account)

    def __unicode__(self):
        return "%(date_sting)s for %(amount)s" % {
                'date_sting' : str(self.date.month) + " '" + str(self.date.year),
                'amount' : str(self.amount),
            }

    class Meta:
        verbose_name = "Credit Card Bill"

    @property
    def is_paid(self):
        return (self.charges.filter(paid=False).count() == 0)

    def total_charges(self):
        total = round(sum(self.charges.all().values_list('amount', flat=True)), 2)
        return total

    def balances(self):
        total = self.total_charges()
        diff = self.amount - total
        if self.amount == total:
            return "Exact"
        elif diff > 0:
            return "$%s short" % str(intcomma(floatformat(diff, 2)))
        else:
            return "$%s over" % str(intcomma(floatformat(-1 * diff, 2)))

    @classmethod
    def get_create_url(cls):
        return reverse("add_ccbill")

    def get_absolute_url(self):
        return reverse("edit_ccbill", kwargs={"id": self.id})


def calc_balance(date, account):
    account = Account.objects.get(title=account)
    ws = Withdrawal.objects.filter(date__lte=date, account=account)
    ds = Deposit.objects.filter(date__lte=date, account=account)
    bal = 0
    for w in ws:
        bal = bal - w.amount
    for d in ds:
        bal = bal + d.amount
    return bal


class Deposit(models.Model):
    """ Into a checking account. """
    title = models.CharField(max_length=250)
    amount = models.FloatField()
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    category = models.ForeignKey(IncomeCategory, blank=True, null=True)
    account = models.ForeignKey(Account, limit_choices_to={'kind':'checking'})
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    do_not_project = models.BooleanField("One-off Event", default=False)

    def balance(self):
        return calc_balance(self.date, self.account.title)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("edit_deposit", kwargs={"id": self.id})

    @classmethod
    def get_create_url(cls):
        return reverse("add_deposit")

    @classmethod
    def search(cls, term):
        # kwargs
        query = Q(title__icontains=term) | Q(notes__icontains=term)
        try:
            num_term = float(term)
            query = query | Q(amount=num_term)
        except ValueError:
            pass
        return cls.objects.filter(query).order_by("-date")


class Withdrawal(models.Model):
    """ Out of a checking account. """
    title = models.CharField(max_length=250)
    amount = models.FloatField()
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ExpenseCategory, blank=True, null=True)
    checkno = models.IntegerField("Check No.", blank=True, null=True)
    account = models.ForeignKey(Account, limit_choices_to={'kind':'checking'})
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    do_not_project = models.BooleanField("One-off Event", default=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("edit_withdrawal", kwargs={"id": self.id})

    @classmethod
    def get_create_url(cls):
        return reverse("add_withdrawal")

    @classmethod
    def search(cls, term):
        # kwargs
        query = Q(title__icontains=term) | Q(notes__icontains=term)
        try:
            num_term = float(term)
            query = query | Q(amount=num_term) | Q(checkno=num_term)
        except ValueError:
            pass
        return cls.objects.filter(query).order_by("-date")

