from django.contrib import admin
from .models import InventoryGroup, Inventory, Shop

admin.site.register([Inventory, InventoryGroup, Shop])
