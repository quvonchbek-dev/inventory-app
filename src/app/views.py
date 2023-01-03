from rest_framework.viewsets import ModelViewSet
from .serializers import (
    InventorySerializer,
    InventoryGroupSerializer,
    Inventory,
    InventoryGroup,
    ShopSerializer,
    Shop,
)
from rest_framework.request import Response
from inventory.custom_methods import IsAuthenticatedCustom
from inventory.utils import get_query, CustomPagination
from django.db.models import Count


class InventoryView(ModelViewSet):
    queryset = Inventory.objects.select("group", "created_by")
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


class InventoryGroupGroupView(ModelViewSet):
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
