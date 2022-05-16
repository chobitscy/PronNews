import datetime
import re
from itertools import groupby
from operator import itemgetter

import requests
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
        update_api = settings.UPDATE
        auth = settings.AUTH
        results = []
        self.items.sort(key=itemgetter('id'))
        for _id, items in groupby(self.items, key=itemgetter('id')):
            urls = [n['print_screen'] for n in items if n['print_screen'] is not None]
            print_screen = []
            for url in urls:
                image_name = re.findall(r'/FC2-PPV-(.*?).jpg', url)[0] + '.jpg'
                response = requests.get(url)
                requests.post(update_api, files={'file': response.content},
                              headers={'Authorization': auth}, data={'name': image_name})
                print_screen.append(image_name)
            results.append({
                'id': _id,
                'print_screen': ','.join(print_screen),
                'update_time': datetime.datetime.now()
            })

        for result in results:
            self.session.query(Video).filter(Video.vid == result['id']).update(
                {Video.print_screen: Video.print_screen + result['print_screen']})
            self.session.commit()
        self.session.close()
