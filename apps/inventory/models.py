from django.core.exceptions import ValidationError
from django.db import models
from django.forms import IntegerField
from django.forms.widgets import Input
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal

# from django.db.models import fields

from ..users.models import User

STATUS = (
    ('Pending', 'Pending'),
    ('Failed', 'Failed'),
    ('Succeed', 'Succeed')
)

METHOD = (
    ('PayPal', 'PayPal'),

)


class PercentInput(Input):
    """ A simple form input for a percentage """
    input_type = 'text'

    def _format_value(self, value):
        if value is None:
            return ''
        return str(int(value * 100))

    def render(self, name, value, attrs=None):
        value = self._format_value(value)
        return super(PercentInput, self).render(name, value, attrs)

    def _has_changed(self, initial, data):
        return super(PercentInput, self)._has_changed(self._format_value(initial), data)


class PercentField(IntegerField):
    """ A field that gets a value between 0 and 1 and displays as a value between 0 and 100"""
    widget = PercentInput(attrs={"class": "percentInput", "size": 4})

    default_error_messages = {
        'positive': _(u'Must be a positive number.'),
    }

    def clean(self, value):
        """
        Validates that the input can be converted to a value between 0 and 1.
        Returns a Decimal
        """
        value = super(PercentField, self).clean(value)
        if value is None:
            return None
        if (value < 0):
            raise ValidationError(self.error_messages['positive'])
        return Decimal("%.2f" % (value / 100.0))


class Scheme(models.Model):
    """
    Record Scheme given to each User.
    """

    user = models.ForeignKey(User, related_name='schemes', on_delete=models.CASCADE)
    cause = models.CharField(max_length=255)
    item = models.CharField(max_length=255)
    discount = PercentField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)


class Payment(models.Model):
    scheme = models.OneToOneField(
        Scheme,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD)
    status = models.CharField(max_length=10, choices=STATUS)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)


import datetime

from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


# from dynamic_search.api import register
# from photos.models import GenericPhoto


class Location(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'Name'))
    address_line1 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line2 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line3 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line4 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    phone_number1 = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u'Phone number'))
    phone_number2 = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u'Phone number'))

    class Meta:
        ordering = ['name']
        verbose_name = _(u'Location')
        verbose_name_plural = _(u'Locations')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('location_view', [str(self.id)])


class ItemTemplate(models.Model):
    description = models.CharField(verbose_name=_(u'Description'), max_length=64)
    brand = models.CharField(verbose_name=_(u'Brand'), max_length=32, null=True, blank=True)
    model = models.CharField(verbose_name=_(u'Model'), max_length=32, null=True, blank=True)
    part_number = models.CharField(verbose_name=_(u'Part number'), max_length=32, null=True, blank=True)
    notes = models.TextField(verbose_name=_(u'Notes'), null=True, blank=True)
    # supplies = models.ManyToManyField('self', null=True, blank=True, verbose_name=_(u'Supplies'))
    # suppliers = models.ManyToManyField('Supplier', null=True, blank=True, verbose_name=_(u'Suppliers'))

    class Meta:
        ordering = ['description']
        verbose_name = _(u'Item template')
        verbose_name_plural = _(u'Item templates')

    @models.permalink
    def get_absolute_url(self):
        return ('template_view', [str(self.id)])

    def __unicode__(self):
        return self.description


class Log(models.Model):
    timedate = models.DateTimeField(auto_now_add=True, verbose_name=_(u'Date & time'))
    action = models.CharField(max_length=32, verbose_name=_(u'Action'))
    description = models.TextField(verbose_name=_(u'Description'), null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __unicode__(self):
        return '%s, %s - %s' % (self.timedate, self.action, self.content_object)

    @models.permalink
    def get_absolute_url(self):
        return ('log_view', [str(self.id)])


class Inventory(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'Name'))
    location = models.ForeignKey(Location, verbose_name=_(u'Location'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _(u'Inventory')
        verbose_name_plural = _(u'Inventories')

    @models.permalink
    def get_absolute_url(self):
        return ('inventory_view', [str(self.id)])

    def __unicode__(self):
        return self.name


import django


class InventoryCheckPoint(models.Model):
    inventory = models.ForeignKey(Inventory, verbose_name=_(u'Inventory'), on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=django.utils.timezone.now, verbose_name=_(u'Date & time'))
    # supplies = models.ManyToManyField(ItemTemplate, null=True, blank=True, through='InventoryCPQty',
    #                                   verbose_name=_(u'Supplies'))


class InventoryCPQty(models.Model):
    supply = models.ForeignKey(ItemTemplate, verbose_name=_(u'Supply'), on_delete=models.CASCADE)
    check_point = models.ForeignKey(InventoryCheckPoint, verbose_name=_(u'Check point'), on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name=_(u'Quantity'))


class InventoryTransaction(models.Model):
    inventory = models.ForeignKey(Inventory, related_name='transactions', verbose_name=_(u'Inventory'),
                                  on_delete=models.CASCADE)
    supply = models.ForeignKey(ItemTemplate, verbose_name=_(u'Supply'), on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name=_(u'Quantity'))
    date = models.DateField(default=django.utils.timezone.now, verbose_name=_(u'Date'))
    notes = models.TextField(null=True, blank=True, verbose_name=_(u'Notes'))

    class Meta:
        verbose_name = _(u'Inventory transaction')
        verbose_name_plural = _(u'Inventory transactions')
        ordering = ['-date', '-id']

    @models.permalink
    def get_absolute_url(self):
        return ('inventory_transaction_view', [str(self.id)])

    def __unicode__(self):
        return "%s: '%s' qty=%s @ %s" % (self.inventory, self.supply, self.quantity, self.date)


class Supplier(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'Name'))
    address_line1 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line2 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line3 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    address_line4 = models.CharField(max_length=64, null=True, blank=True, verbose_name=_(u'Address'))
    phone_number1 = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u'Phone number'))
    phone_number2 = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u'Phone number'))
    notes = models.TextField(null=True, blank=True, verbose_name=(u'Notes'))

    class Meta:
        ordering = ['name']
        verbose_name = _(u'Supplier')
        verbose_name_plural = _(u'Suppliers')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('supplier_view', [str(self.id)])

# register(ItemTemplate, _(u'Templates'), ['description', 'brand', 'model', 'part_number', 'notes'])
# register(Location, _(u'Locations'),
#          ['name', 'address_line1', 'address_line2', 'address_line3', 'address_line4', 'phone_number1', 'phone_number2'])
# register(Inventory, _(u'Inventory'), ['name', 'location__name'])
# register(Supplier, _(u'Supplier'),
#          ['name', 'address_line1', 'address_line2', 'address_line3', 'address_line4', 'phone_number1', 'phone_number2',
#           'notes'])
