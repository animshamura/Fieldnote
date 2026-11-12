from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=80, unique=True)
    industry = models.CharField(max_length=80, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "tenant"

    def __str__(self):
        return self.name
