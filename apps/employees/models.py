from django.db import models
from django.conf import settings

# Create your models here.
class Emplyee(models.Model):
    odoo_id = models.IntegerField(unique=True)
    user   = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                    on_delete=models.SET_NULL,
                                    null=True, related_name='user_employee')
    name = models.TextField()
    license_plate = models.TextField()

    def __str__(self) -> str:
        return self.name
