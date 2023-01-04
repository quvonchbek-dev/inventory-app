from rest_framework.viewsets import ModelViewSet

from app.models import Invoice, Shop, Inventory, InventoryGroup, InvoiceItem
from .serializers import (
    InventorySerializer,
    InventoryGroupSerializer,
    ShopSerializer,
    InvoiceSerializer,
    InventoryWithSumSerializer,
    ShopWithAmountSerializer,
)
from rest_framework.response import Response
from inventory.custom_methods import IsAuthenticatedCustom
from inventory.utils import get_query, CustomPagination
from django.db.models import Count, Sum, F
from django.db.models.functions import Coalesce, TruncMonth
from user.models import CustomUser
import csv
import codecs


class InventoryView(ModelViewSet):
    queryset = Inventory.objects.all().select_related("group", "created_by")
    serializer_class = InventorySerializer
    permission_classes = (IsAuthenticatedCustom,)
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.queryset.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        result = self.queryset(**data)
        if keyword:
            search_fields = [
                "code",
                "created_by__full_name",
                "created_by__email",
                "group__name",
                "name",
            ]
            query = get_query(keyword, search_fields)
            return result.filter(query)
        return result

    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)


class InventoryGroupView(ModelViewSet):
    queryset = InventoryGroup.objects.select_related(
        "group", "created_by"
    ).prefetch_related("inventories")
    serializer_class = InventoryGroupSerializer
    permission_classes = (IsAuthenticatedCustom,)
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.queryset.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        result = self.queryset(**data)
        if keyword:
            search_fields = [
                "created_by__full_name",
                "created_by__email",
                "name",
            ]
            query = get_query(keyword, search_fields)
            return result.filter(query)
        return result.annotate(total_items=Count("inventories"))

    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)


class ShopView(ModelViewSet):
    queryset = Shop.objects.select_related("created_by")
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticatedCustom,)
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.queryset.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        result = self.queryset(**data)
        if keyword:
            search_fields = [
                "created_by__full_name",
                "created_by__email",
                "name",
            ]
            query = get_query(keyword, search_fields)
            return result.filter(query)
        return result

    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)


class InvoiceView(ModelViewSet):
    queryset = Invoice.objects.select_related("created_by", "shop").prefetch_related(
        "invoice_items"
    )
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticatedCustom,)
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.method.lower() != "get":
            return self.queryset

        data = self.queryset.query_params.dict()
        data.pop("page")
        keyword = data.pop("keyword", None)
        result = self.queryset(**data)
        if keyword:
            search_fields = [
                "created_by__fullname",
                "created_by__email",
                "name",
            ]
            query = get_query(keyword, search_fields)
            return result.filter(query)
        return result

    def create(self, request, *args, **kwargs):
        request.data.update({"created_by_id": request.user.id})
        return super().create(request, *args, **kwargs)


class SummaryView(ModelViewSet):
    http_method_names = [
        "get",
    ]
    permission_classes = (IsAuthenticatedCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        total_inventory = InventoryView.queryset.filter(remaining_gt=0).count()
        totat_group = InventoryGroupView.queryset.count()
        total_shop = ShopView.queryset.count()
        total_user = CustomUser.objects.filter(is_superuser=False).count()

        return Response(
            {
                "total_inventory": total_inventory,
                "totat_group": totat_group,
                "total_shop": total_shop,
                "total_user": total_user,
            }
        )


class SalePerformanceView(ModelViewSet):
    http_method_names = [
        "get",
    ]
    permission_classes = (IsAuthenticatedCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        query_data = request.query_params.dict()
        total = query_data.get("total", None)
        query = self.queryset
        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)
            if start_date:
                query = query.filter(
                    inventory_invoices__created_at__range=[start_date, end_date]
                )

        items = query.annotate(
            sum_of_item=Coalesce(Sum("inventory_invoices__quantity"), 0)
        ).order("-sum_of_item")[0:10]

        response_data = InventoryWithSumSerializer(items, many=True).data
        return Response(response_data)


class SaleByShopView(ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (IsAuthenticatedCustom,)
    queryset = InventoryView.queryset

    def list(self, request, *args, **kwargs):
        query_data = request.query_params.dict()
        total = query_data.get("total", None)
        monthly = query_data.get("monthly", None)
        query = ShopView.queryset

        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)

            if start_date:
                query = query.filter(
                    sale_shop__created_at__range=[start_date, end_date]
                )
        if monthly:
            shops = (
                query.annotate(month=TruncMonth("created_at"))
                .values("month", "name")
                .annotate(
                    amount_total=Sum(
                        F("sale_shop__invoice_items__quantity")
                        * F("sale_shop__invoice_items__amount")
                    )
                )
            )
        else:
            shops = query.annotate(
                amount_total=Sum(
                    F("sale_shop__invoice_items__quantity")
                    * F("sale_shop__invoice_items__amount")
                )
            ).order_by("-amount_total")
        response_data = ShopWithAmountSerializer(shops, many=True).data
        return Response(response_data)


class PurchaseView(ModelViewSet):
    http_method_names = ["get"]
    permission_classes = (IsAuthenticatedCustom,)
    queryset = InvoiceView.queryset

    def list(self, request, *args, **kwargs):
        query_data = request.query_params.dict()
        total = query_data.get("total", None)
        query = InvoiceItem.objects.select_related("invoice", "item")

        if not total:
            start_date = query_data.get("start_date", None)
            end_date = query_data.get("end_date", None)

            if start_date:
                query = query.filter(created_at__range=[start_date, end_date])
        query = query.aggregate(
            amount_total=Sum(F("amount") * F("quantity")), total=Sum("quantity")
        )
        c = query.get("amount_total")
        return Response(
            {
                "price": "0.00" if not c else c,
                "count": 0 if not query.get("total") else query.get("total"),
            }
        )


class InventoryCSVLoaderView(ModelViewSet):
    http_method_names = ["post"]
    queryset = InventoryView.queryset
    permission_classes = (IsAuthenticatedCustom,)
    serializer_class = InventoryGroupSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.FILES["data"]
        except Exception:
            raise Exception("You need provide inventory CSV")

        inventory_items = []
        try:
            csv_reader = csv.reader(codecs.iterdecode(data, "utf-8"))
            for row in csv_reader:
                if not row[0]:
                    continue
                inventory_items.append(
                    {
                        "group_id": row[0],
                        "total": row[1],
                        "name": row[2],
                        "price": row[3],
                        "photo": row[4],
                        "added_by_id": request.user.id,
                    }
                )
        except csv.Error as e:
            raise Exception(e)

        if not inventory_items:
            raise Exception("CSV file can't be empty")

        data_validation = self.serializer_class(data=inventory_items, many=True)
        data_validation.is_valid(raise_exception=True)
        data_validation.save()

        return Response({"success": "Inventory Items added succesfully"})
