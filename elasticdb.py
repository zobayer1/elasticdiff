from elasticsearch import Elasticsearch


class ElasticDb:

    def __init__(self, conf):
        print(conf)
        self.db = Elasticsearch([{"host": conf.get('host', 'localhost'), "port": conf.get('port', 9200)}],
                                sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=60,
                                )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self
