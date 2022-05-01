import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
from PronNews.model.product import Product
from PronNews.model.todo import Todo
from PronNews.model.video import Video


class Pipeline(object):

    def __init__(self):
        config = settings.MYSQL
        engine_config = 'mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8' % (
            config['user'], config['passwd'], config['host'], config['port'], config['db'])
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)

    def close_spider(self, spider):
        pid_list = [{'id': n, 'state': 0} for n in set([x['id'] for x in self.items])]
        self.session.bulk_update_mappings(Product, pid_list)
        self.session.commit()

        vid_list = []
        for item in self.items:
            vid_list.extend(item['vid'])
        result = self.session.query(Video).filter(Video.vid.in_(vid_list)).with_entities(Video.vid).all()
        result = [x[0] for x in result]
        result = [n for n in vid_list if n not in result]
        self.items = [{'vid': n, 'create_time': datetime.datetime.now()} for n in result]
        self.session.bulk_insert_mappings(Todo, self.items)
        self.session.commit()
        self.session.close()
