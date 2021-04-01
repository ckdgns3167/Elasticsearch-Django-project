from datetime import datetime

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

import json

from elasticsearch import Elasticsearch, helpers

from common.models import IndexingHistory

DEFAULT_IP = '192.168.1.44'
DEFAULT_PORT = '9200'


@csrf_exempt
def check_elasticsearch_connection(request):
    es_ip = request.POST.get('es_ip')
    es_port = request.POST.get('es_port')

    if str(es_ip).strip() == '':
        es_ip = DEFAULT_IP
    if str(es_port).strip() == '':
        es_port = DEFAULT_PORT

    elastic = Elasticsearch(['http://' + es_ip + ':' + es_port], verify_certs=True)

    if elastic.ping():
        return JsonResponse({'result': True})
    else:
        return JsonResponse({'result': False})


@csrf_exempt
def detect_list_in_json(request):
    file = request.FILES.get('file')
    try:
        json_data = json.loads(file.read())
        # 일단은 json이 최초 { 로 감싸진 것만 통과, 만약 [ 으로 감싸진 것은 제외시킴.
        if str(type(json_data)) != "<class 'dict'>":
            raise Exception
    except Exception:
        return JsonResponse({'result': False, 'msg': '잘못된 json 파일입니다.'})

    lists = []
    for k, v in json_data.items():
        if str(type(v)) == "<class 'list'>":
            lists.append(k)

    if len(lists) == 0:
        return JsonResponse({'result': False, 'msg': '저장시킬 수 있는 객체를 발견하지 못했습니다.'})
    else:
        return JsonResponse({'result': True, 'lists': lists, 'msg': '저장시킬 수 있는 객체를 발견하였습니다.'})


@csrf_exempt
def save_the_data_in_elastic(request):
    file = request.FILES.get('file')
    index_prefix = request.POST.get('index_prefix')
    es_ip = request.POST.get('es_ip')
    es_port = request.POST.get('es_port')

    # 파일로부터 JSON 데이터 가져옴.
    json_data = json.loads(file.read())

    # 엘라스틱 구동
    elastic = Elasticsearch(['http://' + es_ip + ':' + es_port], verify_certs=True)

    if elastic.ping():
        for k, v in json_data.items():
            if str(type(v)) == "<class 'list'>":

                index_name = 'raw-' + index_prefix + '-' + k
                docs = []

                index_id = 1
                for item in v:
                    item["@timestamp"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    docs.append({
                        '_index': index_name,
                        '_id': index_id,
                        '_source': item
                    })
                    index_id = index_id + 1
                try:
                    helpers.bulk(elastic, docs)
                    IndexingHistory.objects.create(index_name=index_name, elastic_server_ip=es_ip, elastic_server_port=es_port)
                except Exception as e:
                    JsonResponse({'result': False, 'msg': e})

        return JsonResponse({'result': True})
    else:
        return JsonResponse({'result': False, 'msg': '엘라스틱서치 연결 불가능'})


@csrf_exempt
def check_elasticsearch_for_duplicate_index_names(request):
    es_ip = request.POST.get('es_ip')
    es_port = request.POST.get('es_port')
    index_prefix = request.POST.get('index_prefix')
    objects_extracted_from_json = request.POST.getlist('objects_extracted_from_json[]')

    if str(es_ip).strip() == '':
        es_ip = DEFAULT_IP
    if str(es_port).strip() == '':
        es_port = DEFAULT_PORT

    elastic = Elasticsearch(['http://' + es_ip + ':' + es_port], verify_certs=True)

    if elastic.ping():
        for item in objects_extracted_from_json:
            if elastic.indices.exists(index='raw-' + index_prefix + '-' + item):
                return JsonResponse({'connection': True, 'already_exists': True})
            else:
                return JsonResponse({'connection': True, 'already_exists': False})
    else:
        return JsonResponse({'connection': False})


@csrf_exempt
def get_pagination_html(request):
    label = request.POST.get('label', None)
    selected_page = request.POST.get('selected_page', None)
    size = request.POST.get('size', None)
    total_page_count = request.POST.get('total_page_count', None)
    selected_data_count = request.POST.get('selected_data_count', None)
    visible_first_page_number = request.POST.get('visible_first_page_number', None)
    visible_last_page_number = request.POST.get('visible_last_page_number', None)
    modal_title = request.POST.get('modal_title', None)
    modal_subtitle = request.POST.get('modal_subtitle', None)

    page_range = list(range(int(visible_first_page_number), int(visible_last_page_number) + 1))

    context = {
        'selected_label': label,
        'selected_page': int(selected_page),
        'selected_data_count': int(selected_data_count),
        'selectable_page_count': int(size),
        'total_page_count': int(total_page_count),
        'visible_first_page_number': visible_first_page_number,
        'visible_last_page_number': visible_last_page_number,
        'page_range': page_range,
        'modal_title': modal_title,
        'modal_subtitle': modal_subtitle,
    }
    pagination_html = render_to_string('pagination.html', context)
    return JsonResponse({'pagination_html': pagination_html})


@csrf_exempt
def get_all_id_in_any_index(request):
    index_name = request.POST.get('index_name')
    category_name = request.POST.get('category_name')
    label = request.POST.get('label')
    total_size = request.POST.get('total_size')

    ids = []

    query_filter = {
        'size': 10000,
        'sort': [{"id": "desc"}],
        'query': {
            "match": {
                category_name: label
            }
        }
    }
    search_result = search(index_name, query_filter)
    source_list = extract_source_in_document(**search_result)
    temp_ids = extract_id_in_source(source_list)
    ids.extend(temp_ids)
    last_id = ids[9999]

    remain = int(total_size) - 10000
    while remain > 0:
        query_filter = {
            'size': 10000 if remain > 10000 else remain,
            'search_after': [last_id],
            'sort': [{"id": "desc"}],
            'track_total_hits': False,
            'query': {
                "match": {
                    category_name: label
                }
            },
        }
        search_result = search(index_name, query_filter)
        source_list = extract_source_in_document(**search_result)
        temp_ids = extract_id_in_source(source_list)
        ids.extend(temp_ids)
        last_id = ids[-1]

        remain = remain - 10000 if remain > 10000 else 0

    return JsonResponse({'ids': ids})


def search(index_name, body):
    elastic = Elasticsearch(['http://' + DEFAULT_IP + ':' + DEFAULT_PORT], verify_certs=True)
    return elastic.search(index=index_name, body=body)


def extract_source_in_document(**dic):
    doc_list = dic['hits']['hits']

    def extract(doc):
        return doc['_source']

    return list(map(extract, doc_list))


def extract_id_in_source(source_list):
    def extract(doc):
        return doc['id']

    return list(map(extract, source_list))
