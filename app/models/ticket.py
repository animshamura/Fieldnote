from django.db import models


class SupportTicket(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    customer = models.ForeignKey("app.Customer", on_delete=models.PROTECT, db_index=True)
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default="Open")
    priority = models.CharField(max_length=20, default="Medium")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "support_ticket"
