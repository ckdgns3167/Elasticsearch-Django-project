import os

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from elasticsearch import Elasticsearch, helpers
import os


def check_elasticsearch_connection():
    es = Elasticsearch(['http://localhost:9200/'], verify_certs=True)

    if not es.ping():
        return JsonResponse({'result': False})
    return JsonResponse({'result': True})


@csrf_exempt
def save_the_data_in_elastic(request):
    file = request.FILES.get('file')
    index_prefix = request.POST.get('index_prefix')
    json_data = json.loads(file.read())
    elastic = Elasticsearch()
    is_connected = json.loads(check_elasticsearch_connection().content.decode('utf-8'))['result']

    if is_connected:
        for k, v in json_data.items():
            if str(type(v)) == "<class 'list'>":

                index_name = index_prefix + '-' + k

                # ndjson 파일 생성.
                f = open(index_name + '.json', 'w', encoding='utf8')

                document_id = 1
                for item in v:
                    f.writelines(['{"index": {"_id": ' + str(document_id) + '}}', '\n'])
                    f.writelines([str(item).replace("'", '"'), '\n'])
                    document_id = document_id + 1

                f.close()

                # 생성된 파일 엘라스틱에 bulk 저장.
                try:
                    helpers.bulk(elastic, bulk_json_data(index_name + '.json', index_name))
                except Exception as e:
                    JsonResponse({'result': False, 'msg': e})

                # 저장시킨 파일은 제거.(임시)
                os.remove(index_name + '.json')

        return JsonResponse({'result': True})
    else:
        return JsonResponse({'result': False, 'msg': '엘라스틱서치 연결 불가능'})


def script_path():
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if os.name == 'posix':  # posix is for macOS or Linux
        path = path + "/"
    else:
        path = path + chr(92)  # backslash is for Windows
    return path


def get_data_from_file(file_name):
    if "/" in file_name or chr(92) in file_name:
        file = open(file_name, encoding="utf8", errors='ignore')
    else:
        file = open(script_path() + str(file_name), encoding="utf8", errors='ignore')
    data = [line.strip() for line in file]
    file.close()
    return data


def bulk_json_data(json_file, _index):
    json_list = get_data_from_file(json_file)
    index_id = 0
    for doc in json_list:
        if '{"index"' not in doc:
            index_id = index_id + 1
            yield {
                "_index": _index,
                "_id": index_id,
                "_source": doc
            }
