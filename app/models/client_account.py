from django.db import models


class ClientAccount(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    customer = models.OneToOneField("app.Customer", on_delete=models.PROTECT, db_index=True)
    email = models.CharField(max_length=160)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "client_account"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "email"), name="uq_client_account_tenant_email"),
        ]
