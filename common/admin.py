from django.contrib import admin
from .models import IndexingHistory


# Register your models here.

class IndexingHistoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(IndexingHistory, IndexingHistoryAdmin)
