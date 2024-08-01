from django.contrib import admin

from .models import Customer, Receipt, Item, ItemInReceipt, ReceiptInReceipt


class CustomerAdmin(admin.ModelAdmin):
	model = Customer


class ReceiptAdmin(admin.ModelAdmin):
	model = Receipt


class ItemAdmin(admin.ModelAdmin):
	model = Item


class ItemInReceiptAdmin(admin.ModelAdmin):
	model = ItemInReceipt


class ReceiptInReceiptAdmin(admin.ModelAdmin):
	model = ReceiptInReceipt


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInReceipt, ItemInReceiptAdmin)
admin.site.register(ReceiptInReceipt, ReceiptInReceiptAdmin)