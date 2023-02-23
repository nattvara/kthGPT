
from opensearchpy import OpenSearch
from config.settings import settings
from typing import List


def clean_response(response: dict, fields: List[str]) -> List[dict]:
    out = []
    hits = response['hits']['hits']
    for hit in hits:
        item = {}
        for field in fields:
            if field not in hit['fields']:
                item[field] = None
            else:
                item[field] = hit['fields'][field][0]
        out.append(item)
    return out


client = client = OpenSearch(
    hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
    http_compress=True,
    http_auth=(settings.OPENSEARCH_USERNAME, settings.OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)
