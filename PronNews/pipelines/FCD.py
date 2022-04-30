import datetime

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
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()

    def process_item(self, item, spider):
        target = self.session.query(Video).filter(Video.vid == item['vid']).one()
        _id = target.id
        if item['create_date'] is not None and target.create_date is None:
            product = self.session.query(Product).filter(Product.name == item['product']).one()
            if product is None:
                pd = Product(item['product'], item['product_home'], None)
                pid = pd.id
                self.session.add(pd)
                self.session.commit()
            else:
                pid = product.id
            self.session.query(Video).filter(Video.id == _id).update({
                Video.screenshot: item['screenshot'],
                Video.thumb: item['thumb'],
                Video.tid: item['tags'],
                Video.create_date: item['create_date'],
                Video.update_time: datetime.datetime.now(),
                Video.pid: pid
            })
            self.session.commit()
        elif item['create_date'] is None:
            self.session.query(Video).filter(Video.id == _id).update({
                Video.state: -1
            })
            self.session.commit()

    def close_spider(self, spider):
        self.session.close()
