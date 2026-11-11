from django.db import models


class ClientInvite(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    customer = models.ForeignKey("app.Customer", on_delete=models.PROTECT, db_index=True)
    email = models.CharField(max_length=160)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "client_invite"
