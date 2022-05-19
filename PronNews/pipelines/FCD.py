import json

from redis import StrictRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
from PronNews.model.product import Product
from PronNews.model.video import Video


class Pipeline(object):

    def __init__(self):
        config = settings.MYSQL
        engine_config = 'mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8' % (
            config['user'], config['passwd'], config['host'], config['port'], config['db'])
        redis_config = settings.REDIS
        self.key = "product_info"
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        self.redis = StrictRedis(host=redis_config['host'], port=redis_config['port'], username=redis_config['user'],
                                 password=redis_config['password'], db=redis_config['db'])

    def process_item(self, item, spider):
        if item['create_date'] is None:
            return
        product = self.session.query(Product).filter(Product.name == item['product']).first()
        if product is None:
            pd = Product(item['product'], item['product_home'], None)
            pid = pd.id
            self.session.add(pd)
            self.session.commit()
            self.redis.rpush(self.key, json.dumps({"pid": pid, "home": pd.home}))
        else:
            pid = product.id
        item['pid'] = pid
        self.session.query(Video).filter(Video.id == item['id']).update({
            'screenshot': item['screenshot'],
            'thumb': item['thumb'],
            'pid': pid,
            'tid': item['tid'],
            'create_date': item['create_date'],
            'update_time': item['update_time']
        })
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()
