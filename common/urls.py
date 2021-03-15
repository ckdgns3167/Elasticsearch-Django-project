from django.conf.urls import url
from .views import *

app_name = 'common'
app_category_name = '공통'

urlpatterns = [
    url(r'^ajax/check_elasticsearch_connection$', check_elasticsearch_connection, name='check_elasticsearch_connection'),
    url(r'^ajax/detect_list_in_json$', detect_list_in_json, name='detect_list_in_json'),
    url(r'^ajax/save_json_to_elasticsearch$', save_the_data_in_elastic, name='save_the_data_in_elastic'),
    url(r'^ajax/check_index_name_in_elastic$', check_index_name_in_elastic, name='check_index_name_in_elastic'),
]