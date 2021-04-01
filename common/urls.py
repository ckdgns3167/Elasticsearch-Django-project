from django.conf.urls import url
from .views import *

app_name = 'common'
app_category_name = '공통'

urlpatterns = [

    # related to saving data.
    url(r'^ajax/check_elasticsearch_connection$', check_elasticsearch_connection, name='check_elasticsearch_connection'),
    url(r'^ajax/detect_list_in_json$', detect_list_in_json, name='detect_list_in_json'),
    url(r'^ajax/save_json_to_elasticsearch$', save_the_data_in_elastic, name='save_the_data_in_elastic'),
    url(r'^ajax/check_elasticsearch_for_duplicate_index_names', check_elasticsearch_for_duplicate_index_names, name='check_elasticsearch_for_duplicate_index_names'),

    # related to getting data.
    url(r'^ajax/get_pagination_html$', get_pagination_html, name='get_pagination_html'),
    url(r'^ajax/get_all_id_in_any_index$', get_all_id_in_any_index, name='get_all_id_in_any_index'),
]