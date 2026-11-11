from django.db import models


class Product(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=80)
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "product"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "sku"), name="uq_product_tenant_sku"),
        ]
