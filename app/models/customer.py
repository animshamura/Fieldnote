from django.db import models


class Customer(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=160, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    company = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "customer"
