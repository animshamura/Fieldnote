from django.db import models


class User(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    username = models.CharField(max_length=80)
    email = models.CharField(max_length=160)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "user"
        constraints = [
            models.UniqueConstraint(fields=("tenant", "username"), name="uq_user_tenant_username"),
            models.UniqueConstraint(fields=("tenant", "email"), name="uq_user_tenant_email"),
        ]
