import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
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
        if len(self.items) == 0:
            self.session.close()
            return

        self.session.bulk_update_mappings(Video, self.items)
        self.session.commit()
        self.session.close()
