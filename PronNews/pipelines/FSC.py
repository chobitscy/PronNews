import datetime
from itertools import groupby
from operator import itemgetter

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

        results = []
        self.items.sort(key=itemgetter('id'))
        for _id, items in groupby(self.items, key=itemgetter('id')):
            results.append({
                'id': _id,
                'print_screen': ','.join([n['print_screen'] for n in items if n['print_screen'] is not None]),
                'update_time': datetime.datetime.now()
            })

        self.session.bulk_update_mappings(Video, results)
        self.session.commit()
        self.session.close()
