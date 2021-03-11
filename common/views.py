from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from elasticsearch import Elasticsearch, helpers

from common.models import IndexingHistory


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

                index_name = index_prefix + '-' + k
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
