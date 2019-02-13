from redisdb import RedisDb
from elasticdb import ElasticDb
from multiprocessing import Pool
from threading import Thread
from utils import *
import argparse
import json


class DataLoadThread(Thread):

    def __init__(self, esdb):
        super(DataLoadThread, self).__init__()
        self.esdb = esdb

    def run(self):
        pass


def process(data):
    return listhash(ordered(data))


def main(conf):
    hash_store = RedisDb(conf['redis'])
    es_source = ElasticDb(conf['elastic']['source'])
    es_target = ElasticDb(conf['elastic']['target'])

    DataLoadThread(es_source).start()
    DataLoadThread(es_target).start()


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configuration', required=True, help='Please specify configuration json')
    args = parser.parse_args()

    with open(args.configuration, 'r', encoding='utf-8') as fin:
        main(json.loads(fin.read()))
