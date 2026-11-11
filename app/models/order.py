from django.db import models


class Order(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    customer = models.ForeignKey("app.Customer", on_delete=models.PROTECT, db_index=True)
    order_number = models.CharField(max_length=60)
    status = models.CharField(max_length=30, default="Pending")
    total_amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "order"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "order_number"), name="uq_order_tenant_number"),
        ]


class OrderItem(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    order = models.ForeignKey("app.Order", on_delete=models.PROTECT, db_index=True, related_name="items")
    product = models.ForeignKey("app.Product", on_delete=models.PROTECT, db_index=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)

    class Meta:
        db_table = "order_item"
