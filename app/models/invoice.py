from django.db import models


class Invoice(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    customer = models.ForeignKey("app.Customer", on_delete=models.PROTECT, db_index=True)
    invoice_number = models.CharField(max_length=60)
    status = models.CharField(max_length=30, default="Draft")
    subtotal = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)
    issue_date = models.DateField()
    due_date = models.DateField()

    class Meta:
        db_table = "invoice"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "invoice_number"), name="uq_invoice_tenant_number"),
        ]


class InvoiceItem(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    invoice = models.ForeignKey("app.Invoice", on_delete=models.PROTECT, db_index=True, related_name="items")
    product = models.ForeignKey("app.Product", on_delete=models.PROTECT, db_index=True)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)

    class Meta:
        db_table = "invoice_item"
