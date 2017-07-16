import datetime

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from ..dashboard import Dashboard
from ..models import Charge


@staff_member_required
def index(request):
    dashboard = Dashboard(year=request.GET.get("year"))

    latest_year = datetime.date.today().year
    years = [latest_year, ]
    
    # If there's data, use it to determine the first
    # year we have a record of.
    first_charge = Charge.objects.filter(date__isnull=False).first()
    if first_charge:
        years = range(datetime.date.today().year, first_charge.date.year - 1, -1)

    return render(request, "index.html", 
        {
            "dashboard": dashboard,
            "years": years,
        })