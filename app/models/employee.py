from django.db import models


class Employee(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    department = models.ForeignKey(
        "app.Department", on_delete=models.PROTECT, null=True, blank=True, db_index=True
    )
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=160, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    position = models.CharField(max_length=80, null=True, blank=True)
    salary = models.FloatField(default=0.0)

    class Meta:
        db_table = "employee"
