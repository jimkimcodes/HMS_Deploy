from django.db import models
from institute.models import Blocks, Officials

# Create your models here.
class WaterCan(models.Model):

    date = models.DateField(null=False)
    block = models.ForeignKey(Blocks,on_delete=models.CASCADE, null=False)
    count = models.IntegerField(null=False)
