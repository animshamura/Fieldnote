from django.db import models


class Subscription(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    billing_cycle = models.CharField(max_length=30, default="Monthly")
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        db_table = "subscription"
