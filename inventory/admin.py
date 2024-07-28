from django.contrib import admin

from .models import Receipt, Item, ItemInReceipt


class ReceiptAdmin(admin.ModelAdmin):
	model = Receipt


class ItemAdmin(admin.ModelAdmin):
	model = Item


class ItemInReceiptAdmin(admin.ModelAdmin):
	model = ItemInReceipt


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInReceipt, ItemInReceiptAdmin)