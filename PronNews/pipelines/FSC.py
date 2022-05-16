import re

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
        self.update_api = settings.UPDATE
        self.auth = settings.AUTH

    def process_item(self, item, spider):
        url = item['print_screen']
        image_name = re.findall(r'/FC2-PPV-(.*?).jpg', url)[0] + '.jpg'
        response = requests.get(url)
        requests.post(self.update_api, files={'file': response.content},
                      headers={'Authorization': self.auth}, data={'name': image_name})
        self.session.query(Video).filter(Video.id == item['id']).update(
            {Video.print_screen: Video.print_screen + image_name})
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()
