import json

from redis import StrictRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings


class Pipeline(object):

    def __init__(self):
        config = settings.MYSQL
        engine_config = 'mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8' % (
            config['user'], config['passwd'], config['host'], config['port'], config['db'])
        redis_config = settings.REDIS
        self.key = "product_vid"
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
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
        self.session.close()
