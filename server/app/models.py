from django.db import models
from user.models import CustomUser
from user.views import add_user_activities


class InventoryGroup(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        null=True,
        related_name="inventory_groups",
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=100, unique=True)
    belongs_to = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="group_relations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"added new group - '{self.name}'"
        if self.pk is not None:
            action = f"update group from '{self.old_name}' to {self.name}"
        super().save(*args, **kwargs)
        add_user_activities(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted group - '{self.name}'"
        super().delete(*args, **kwargs)
        add_user_activities(created_by, activity=action)

    def __str__(self) -> str:
        return self.name


class Inventory(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        null=True,
        related_name="inventory_items",
        on_delete=models.SET_NULL,
    )
    code = models.CharField(max_length=10, unique=True, null=True)
    photo = models.TextField(blank=True, null=True)
    gruop = models.ForeignKey(
        InventoryGroup, related_name="inventories", null=True, on_delete=models.SET_NULL
    )
    total = models.PositiveIntegerField()
    remaining = models.PositiveBigIntegerField(null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.remaining = self.total
        super().save(*args, **kwargs)
        if is_new:
            c = "0" * (6 - len(str(self.id)))
            self.code = f"BOSE{c}{self.id}"
            self.save()

    action = f"added inventory item with code - {code}"

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted inventory - '{self.code}'"
        super().delete(*args, **kwargs)
        add_user_activities(created_by, activity=action)

    def __str__(self) -> str:
        return f"{self.name} - {self.code}"


class Shop(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        null=True,
        related_name="shops",
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"added new shop - '{self.name}'"
        if self.pk is not None:
            action = f"update shop from '{self.old_name}' to {self.name}"
        super().save(*args, **kwargs)
        add_user_activities(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted shop - '{self.name}'"
        super().delete(*args, **kwargs)
        add_user_activities(created_by, activity=action)

    def __str__(self) -> str:
        return self.name


class Invoice(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        null=True,
        related_name="invoices",
        on_delete=models.SET_NULL,
    )
    shop = models.ForeignKey(
        Shop, related_name="sale_shop", null=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        action = f"added new invoice"
        super().save(*args, **kwargs)
        add_user_activities(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted invoice - '{self.id}'"
        super().delete(*args, **kwargs)
        add_user_activities(created_by, activity=action)

    def __str__(self) -> str:
        return self.name


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="invoice_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Inventory,
        related_name="inventory_invoices",
        null=True,
        on_delete=models.SET_NULL,
    )
    item_name = models.CharField(max_length=255, null=True)
    item_code = models.CharField(max_length=20, null=True)
    quantity = models.PositiveIntegerField()
    amount = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.item.remaining < self.quantity:
            raise Exception(
                f"Item with code {self.item.code} does not haveenough quantity."
            )
        self.item_name = self.item.name
        self.item_code = self.item.code

        self.amount = self.quantity * self.item.price
        self.item.remaining = self.item.remaining - self.quantity
        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_code} - {self.quantity}"
