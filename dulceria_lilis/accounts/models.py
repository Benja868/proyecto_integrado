from django.conf import settings
from django.db import models
from organizations.models import Organization

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"
