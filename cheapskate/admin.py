from django.contrib import admin
from .models import (ExpenseCategory, IncomeCategory, 
	Charge, CCBill, Deposit, Withdrawal, Account)

def pay_bill(modeladmin, request, queryset):
	for q in queryset:
		q.charges.all().update(paid=True)
pay_bill.short_description = "Pay this bill"

def unpay_bill(modeladmin, request, queryset):
	for q in queryset:
		q.charges.all().update(paid=True)
unpay_bill.short_description = "Mark bill as unpaid"

class AccountAdmin(admin.ModelAdmin):
	list_display = ['title', 'bank', 'kind']

class ChargeAdmin(admin.ModelAdmin):
	list_display = ['title', 'amount', 'date', 'category', 'paid', 
					'account', 'is_one_off']
	list_filter = ['category', 'date', 'paid', 'account', 'is_one_off']
	search_fields = ['title', 'amount',]
	list_editable = ['category',]
	ordering = ['-date']

class CCBillAdmin(admin.ModelAdmin):
	list_display = ['date', 'amount', 'total_charges', 'account']
	list_filter = ['account',]
	filter_vertical = ['charges',]
	actions = [pay_bill, unpay_bill]

class DepositAdmin(admin.ModelAdmin):
	list_display = ['title', 'amount', 'date', 'category', 'account',
					'is_one_off']
	list_editable = ['category',]
	list_filter = ['date', 'account', 'category', 'is_one_off']
	ordering = ['-date']
	search_fields = ['title', 'amount']

class WithdrawalAdmin(admin.ModelAdmin):
	list_display = ['title', 'amount', 'date', 'category', 'account', 'is_one_off']
	list_editable = ['category',]
	list_filter = ['date','account', 'category', 'is_one_off']
	ordering = ['-date']
	search_fields = ['title', 'amount']

admin.site.register(Account, AccountAdmin)
admin.site.register(ExpenseCategory)
admin.site.register(IncomeCategory)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(CCBill, CCBillAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)