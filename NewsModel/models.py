from django.db import models

# Create your models here.
class news(models.Model):
    source=models.URLField()
    url=models.URLField()
    image_url=models.URLField()
    title=models.CharField(max_length=50)
    content=models.TextField()
    
