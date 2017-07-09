import datetime

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from ..dashboard import Dashboard
from ..models import Charge


@staff_member_required
def index(request):
    dashboard = Dashboard(year=request.GET.get("year"))
    years = range(datetime.date.today().year, Charge.objects.filter(date__isnull=False).first().date.year - 1, -1)
    return render(request, "index.html", 
        {
            "dashboard": dashboard,
            "years": years,
        })