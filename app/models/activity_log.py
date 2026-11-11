from django.db import models


class ActivityLog(models.Model):
    tenant = models.ForeignKey("app.Tenant", on_delete=models.PROTECT, db_index=True)
    action = models.CharField(max_length=200)
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "activity_log"
