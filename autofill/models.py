from django.db import models
from django.contrib.auth.models import User

class AutoFill(models.Model):
    user = models.ForeignKey(User)
    field = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('user', 'field')
