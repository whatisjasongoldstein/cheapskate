import datetime
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import slugify

from ..models import IncomeCategory, ExpenseCategory


@staff_member_required
def income_category(request, slug):
    year = request.GET.get('year') or datetime.date.today().year

    rough_cats = IncomeCategory.objects.all().values('title', 'id')
    cat_dict = {}
    for r in rough_cats:
        cat_dict[slugify(r['title'])] = r['id']

    cat_id = cat_dict.get(slug)
    if not cat_id:
        raise Http404
    category = IncomeCategory.objects.get(id=cat_id)
    objs = category.deposit_set.filter(date__year=year)
    total = sum([obj.amount for obj in objs])

    return render(request, "category.html", {
            'objs': objs,
            'category': category,
            'year': year,
            'total': total,
        })


@staff_member_required
def expense_category(request, slug):
    year = request.GET.get('year') or datetime.date.today().year

    rough_cats = ExpenseCategory.objects.all().values('title', 'id')
    cat_dict = {}
    for r in rough_cats:
        cat_dict[slugify(r['title'])] = r['id']

    cat_id = cat_dict.get(slug)
    if not cat_id:
        raise Http404
    category = ExpenseCategory.objects.get(id=cat_id)
    objs = list(category.charge_set.filter(date__year=year)) + list(category.withdrawal_set.filter(date__year=year))
    objs = sorted(objs, key=lambda obj: obj.date)

    total = sum([obj.amount for obj in objs])

    return render(request, "category.html", {
            'objs': objs,
            'category': category,
            'year': year,
            'total': total,
        })