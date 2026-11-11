from django.db import models


class Department(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "department"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "name"), name="uq_department_tenant_name"),
        ]
