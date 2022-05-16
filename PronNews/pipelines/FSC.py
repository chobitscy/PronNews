import datetime
import re

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings


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
        if url is None:
            return
        update_time = datetime.datetime.now()
        image_name = re.findall(r'/FC2-PPV-(.*?).jpg', url)[0] + '.jpg'
        response = requests.get(url)
        requests.post(self.update_api, files={'file': response.content},
                      headers={'Authorization': self.auth}, data={'name': image_name})
        sql = "UPDATE video SET print_screen = IFNULL(CONCAT(print_screen,'%s'),'%s'), update_time = '%s' " \
              "WHERE id = %s" % (',' + image_name, image_name, update_time, item['id'])
        self.session.execute(sql)
        self.session.commit()

    def close_spider(self, spider):
        self.session.close()
