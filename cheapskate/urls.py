from __future__ import absolute_import

from django.urls import include, path

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from .views import dashboard_views
from .views import list_views
from .views import form_views
from .views import legacy_views


admin.autodiscover()


urlpatterns = [
    path('', dashboard_views.index, name='index'),

    path('charges/', list_views.ChargeListView.as_view(), name='charge_list'),
    path('withdrawals/', list_views.WithdrawalListView.as_view(), name='withdrawal_list'),
    path('deposits/', list_views.DepositListView.as_view(), name='deposit_list'),
    path('credit-card-bills/', list_views.CCBillListView.as_view(), name='ccbill_list'),

    path('charges/add/', form_views.ChargeView.as_view(), name='add_charge'),
    path('charges/<int:id>/', form_views.ChargeView.as_view(), name='edit_charge'),

    path('withdrawals/add/', form_views.WithdrawalView.as_view(), name='add_withdrawal'),
    path('withdrawals/<int:id>/', form_views.WithdrawalView.as_view(), name='edit_withdrawal'),

    path('deposits/add/', form_views.DepositView.as_view(), name='add_deposit'),
    path('deposits/<int:id>/', form_views.DepositView.as_view(), name='edit_deposit'),

    path('credit-card-bills/add/', form_views.CCBillView.as_view(), name='add_ccbill'),
    path('credit-card-bills/<int:id>/', form_views.CCBillView.as_view(), name='edit_ccbill'),

    # To refactor
    path('income/<slug:slug>/', legacy_views.income_category, name="category"),
    path('expense/<slug:slug>/', legacy_views.expense_category, name="category"),

    path('', include('django.contrib.auth.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]