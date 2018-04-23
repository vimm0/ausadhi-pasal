from __future__ import absolute_import
from django.contrib import admin

from django.contrib import admin

from .models import Inventory, ItemTemplate, Location, Log, Supplier
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    fields = ('amount', 'method', 'status')


class ItemTemplateAdmin(admin.ModelAdmin):
    pass
    # filter_horizontal = ('supplies', 'suppliers')


admin.site.register(Location)
admin.site.register(Log)
admin.site.register(ItemTemplate, ItemTemplateAdmin)
admin.site.register(Inventory)
admin.site.register(Supplier)
admin.site.register(Payment, PaymentAdmin)
