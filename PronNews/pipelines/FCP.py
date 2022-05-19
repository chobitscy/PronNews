from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
from PronNews.model.product import Product


class Pipeline(object):

    def __init__(self):
        config = settings.MYSQL
        engine_config = 'mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8' % (
            config['user'], config['passwd'], config['host'], config['port'], config['db'])
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    def process_item(self, item, spider):
        self.session.query(Product).filter(Product.id == item['id']).update({
            'avatar': item['avatar'],
            'works': item['works'],
            'fans': item['fans'],
            'update_time': item['update_time']
        })
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()
