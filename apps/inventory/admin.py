from django.contrib import admin

from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    fields = ('amount', 'method', 'status')


admin.site.register(Payment, PaymentAdmin)
