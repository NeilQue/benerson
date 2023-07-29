from django.contrib import admin

from .models import Receipt, Item


class ReceiptAdmin(admin.ModelAdmin):
	model = Receipt


class ItemAdmin(admin.ModelAdmin):
	model = Item


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Item, ItemAdmin)