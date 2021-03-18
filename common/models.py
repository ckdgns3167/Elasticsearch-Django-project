from django.db import models


# Create your models here.
class IndexingHistory(models.Model):
    id = models.AutoField(primary_key=True)
    index_name = models.CharField(max_length=200)
    elastic_server_ip = models.CharField(max_length=20, default='127.0.0.1')
    elastic_server_port = models.CharField(max_length=10, default='9200')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.index_name
