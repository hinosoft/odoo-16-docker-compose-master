from django.db import models
from django.conf import settings

# Create your models here.
class Tracking(models.Model):
    code = models.IntegerField()
    time= models.DateTimeField()
    note = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return '{}-{}'.format(self.code, self.time.strftime('%Y-%m-%d %H:%M%s'))
