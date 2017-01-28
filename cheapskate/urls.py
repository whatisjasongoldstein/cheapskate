from __future__ import absolute_import

from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from cheapskate import views

admin.autodiscover()


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^charges/$', views.ChargeListView.as_view(), name='charge_list'),
    url(r'^withdrawals/$', views.WithdrawalListView.as_view(), name='withdrawal_list'),
    url(r'^deposits/$', views.DepositListView.as_view(), name='deposit_list'),
    url(r'^credit-card-bills/$', views.CCBillListView.as_view(), name='ccbill_list'),

    url(r'^charges/add/$', views.ChargeView.as_view(), name='add_charge'),
    url(r'^charges/(?P<id>[\d]+)/$', views.ChargeView.as_view(), name='edit_charge'),

    url(r'^withdrawals/add/$', views.WithdrawalView.as_view(), name='add_withdrawal'),
    url(r'^withdrawals/(?P<id>[\d]+)/$', views.WithdrawalView.as_view(), name='edit_withdrawal'),

    url(r'^deposits/add/$', views.DepositView.as_view(), name='add_deposit'),
    url(r'^deposits/(?P<id>[\d]+)/$', views.DepositView.as_view(), name='edit_deposit'),

    url(r'^credit-card-bills/add/$', views.CCBillView.as_view(), name='add_ccbill'),
    url(r'^credit-card-bills/(?P<id>[\d]+)/$', views.CCBillView.as_view(), name='edit_ccbill'),

    # To refactor
    url(r'^income/(?P<slug>[-\w\d]+)/$', views.income_category, name="category"),
    url(r'^expense/(?P<slug>[-\w\d]+)/$', views.expense_category, name="category"),

    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
