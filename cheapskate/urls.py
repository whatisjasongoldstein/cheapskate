from __future__ import absolute_import

from django.conf.urls import include, url

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
    url(r'^$', dashboard_views.index, name='index'),
    url(r'^charges/$', list_views.ChargeListView.as_view(), name='charge_list'),
    url(r'^withdrawals/$', list_views.WithdrawalListView.as_view(), name='withdrawal_list'),
    url(r'^deposits/$', list_views.DepositListView.as_view(), name='deposit_list'),
    url(r'^credit-card-bills/$', list_views.CCBillListView.as_view(), name='ccbill_list'),

    url(r'^charges/add/$', form_views.ChargeView.as_view(), name='add_charge'),
    url(r'^charges/(?P<id>[\d]+)/$', form_views.ChargeView.as_view(), name='edit_charge'),

    url(r'^withdrawals/add/$', form_views.WithdrawalView.as_view(), name='add_withdrawal'),
    url(r'^withdrawals/(?P<id>[\d]+)/$', form_views.WithdrawalView.as_view(), name='edit_withdrawal'),

    url(r'^deposits/add/$', form_views.DepositView.as_view(), name='add_deposit'),
    url(r'^deposits/(?P<id>[\d]+)/$', form_views.DepositView.as_view(), name='edit_deposit'),

    url(r'^credit-card-bills/add/$', form_views.CCBillView.as_view(), name='add_ccbill'),
    url(r'^credit-card-bills/(?P<id>[\d]+)/$', form_views.CCBillView.as_view(), name='edit_ccbill'),

    # To refactor
    url(r'^income/(?P<slug>[-\w\d]+)/$', legacy_views.income_category, name="category"),
    url(r'^expense/(?P<slug>[-\w\d]+)/$', legacy_views.expense_category, name="category"),

    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]