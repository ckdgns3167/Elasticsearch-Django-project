from django.conf.urls import url
from .views import *

app_name = 'common'
app_category_name = '공통'

urlpatterns = [

    url(r'^ajax/ndjson_file/save_in_elastic$', save_the_data_in_elastic, name='save_the_data_in_elastic'),
]