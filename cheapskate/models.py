import datetime
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

ACCOUNT_CHOICES = (
    ('checking', 'Checking'),
    ('cc', 'Credit Card')
)


class Account(models.Model):
    """ A checking or credit card account """
    title = models.CharField(max_length=255)
    bank = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=ACCOUNT_CHOICES)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ('title', )


class ExpenseCategory(Category):
    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"


class IncomeCategory(Category):
    class Meta:
        verbose_name = "Income Category"
        verbose_name_plural = "Income Categories"


class Charge(models.Model):
    """
    A credit card change.
    """
    title = models.CharField(max_length=250)
    amount = models.FloatField()
    category = models.ForeignKey(ExpenseCategory, null=True, on_delete=models.SET_NULL)
    account = models.ForeignKey(Account, limit_choices_to={'kind':'cc'}, null=True,
        on_delete=models.SET_NULL)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    paid = models.BooleanField(default=False)
    lost = models.BooleanField(default=False)
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    is_one_off = models.BooleanField("One-off Event", default=False)

    def __str__(self):
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
    account = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)

    def __str__(self):
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
        total = (self.charges.all()
                     .aggregate(models.Sum("amount"))["amount__sum"] or 0)
        return round(total, 2)

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


class Deposit(models.Model):
    """ Into a checking account. """
    title = models.CharField(max_length=250)
    amount = models.FloatField()
    category = models.ForeignKey(IncomeCategory, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, default="")
    account = models.ForeignKey(Account, null=True,
        limit_choices_to={'kind':'checking'}, on_delete=models.SET_NULL)
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    is_one_off = models.BooleanField("One-off Event", default=False)

    def __str__(self):
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
    category = models.ForeignKey(ExpenseCategory, blank=True, null=True,
        on_delete=models.SET_NULL)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    checkno = models.IntegerField("Check No.", blank=True, null=True)
    account = models.ForeignKey(Account, null=True,
        limit_choices_to={'kind':'checking'}, on_delete=models.SET_NULL)
    document = models.FileField(upload_to='copies/%Y/%m/', blank=True, null=True)
    is_one_off = models.BooleanField("One-off Event", default=False)

    def __str__(self):
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

