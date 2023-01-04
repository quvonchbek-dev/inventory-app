from django.urls import path, include

from .views import (
    ShopView,
    InvoiceView,
    SummaryView,
    PurchaseView,
    InventoryView,
    SaleByShopView,
    SalePerformanceView,
    InventoryGroupView,
    InventoryCSVLoaderView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register("shop", ShopView, "shop")
router.register("invoice", InvoiceView, "invoice")
router.register("summary", SummaryView, "summary")
router.register("purchase", PurchaseView, "purchase")
router.register("inventory", InventoryView, "inventory")
router.register("inventory-group", InventoryGroupView, "inventory group")
router.register("inventory-csv", InventoryCSVLoaderView, "inventory csv")

router.register("sale-by-shop", SaleByShopView, "sale by shop")
router.register("sale-performance", SalePerformanceView, "sale performance")
urlpatterns = [path("", include(router.urls))]
