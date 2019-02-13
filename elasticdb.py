from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan


class ElasticDb:

    def __init__(self, conf, scroll_time='1m', scroll_size=1000):
        self.db = Elasticsearch([{"host": conf.get('host', 'localhost'), "port": conf.get('port', 9200)}],
                                sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=60,
                                )
        self.index = conf['index']
        self.type = conf.get('type', None)
        self.scroll_time = scroll_time
        self.scroll_size = scroll_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def scan(self):
        yield from scan(self.db, scroll=self.scroll_time, size=self.scroll_size, index=self.index, doc_type=self.type)
