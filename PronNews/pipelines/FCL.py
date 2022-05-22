import json

from redis import StrictRedis

from PronNews import settings


class Pipeline(object):

    def __init__(self):
        redis_config = settings.REDIS
        self.key = "product_vid"
        self.redis = StrictRedis(host=redis_config['host'], port=redis_config['port'], username=redis_config['user'],
                                 password=redis_config['password'], db=redis_config['db'])

    def process_item(self, item, spider):
        vid_list = list(item['vid'])
        for vid in vid_list:
            self.redis.rpush(self.key, json.dumps({
                'pid': item['id'],
                'vid': vid
            }))

    def close_spider(self, spider):
        self.redis.close()
