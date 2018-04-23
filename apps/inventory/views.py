from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404

from django.views.generic import TemplateView, DetailView

from apps.inventory.models import InventoryItem
from apps.product.models import Product


class Home(TemplateView):
    template_name = 'inventory/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = ContentType.objects.get_for_model(Product)
        context['item_type'] = ContentType.objects.get_for_model(Product)
        context['item_list'] = InventoryItem.objects.filter(content_type=content_type)
        return context
