from redisdb import RedisDb
from elasticdb import ElasticDb
from threading import Thread
from utils import *
import argparse
import json


__include_index = False


class DataLoadThread(Thread):

    def __init__(self, esdb, redisdb):
        super(DataLoadThread, self).__init__()
        self.esdb = esdb
        self.redisdb = redisdb

    def run(self):
        for hit in self.esdb.scan():
            key, value = process(hit)
            self.redisdb.atomic_update(key, value)


def process(hit):
    data = hit['_source']
    if __include_index:
        data['_id'] = hit['_id']
    uid = hit['_index'] + ':' + hit['_type'] + ':' + hit['_id']
    return listhash(ordered(data)), uid


def main(conf):
    global __include_index
    __include_index = conf['elastic'].get('include_id', False)

    scroll_time = conf['elastic'].get('scroll_time', u'1m')
    scroll_size = conf['elastic'].get('scroll_size', 1000)

    hash_store = RedisDb(conf['redis'])
    es_source = ElasticDb(conf['elastic']['source'], scroll_time=scroll_time, scroll_size=scroll_size)
    es_target = ElasticDb(conf['elastic']['target'], scroll_time=scroll_time, scroll_size=scroll_size)

    source_thread = DataLoadThread(es_source, hash_store)
    target_thread = DataLoadThread(es_target, hash_store)

    source_thread.start()
    target_thread.start()

    source_thread.join()
    target_thread.join()

    total_miss = 0
    for dt in hash_store.find_diff():
        print(dt)
        total_miss += 1

    print(f'Total {total_miss} record(s) mismatched')

    hash_store.reset()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help='Please specify configuration json')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as fin:
        main(json.loads(fin.read()))
