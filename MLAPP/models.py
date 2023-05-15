from django.db import models

# Create your models here.
class Dataset(models.Model):
    dataset=models.FileField(null=True)