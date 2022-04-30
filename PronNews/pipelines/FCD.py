import datetime

import pymysql
from scrapy import Spider

from PronNews.utils import get_snowflake_uuid


class Pipeline(object):

    def __init__(self, spider: Spider):
        config = spider.settings.get('MYSQL')
        self.connect = pymysql.connect(host=config['host'], user=config['user'], passwd=config['passwd'],
                                       db=config['db'])
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        result = self.cursor.execute("SELECT id,create_date from video WHERE vid = '%s'" % item['vid'])
        _id = result[0][0]
        create_date = result[0][1]
        if item['create_date'] is not None and create_date is None:
            pq = self.cursor.execute("SELECT id FROM product WHERE name = '%s'" % item['product'])
            pid = pq[0][0]
            if pq is None:
                now = datetime.datetime.now()
                pid = get_snowflake_uuid()
                sql = """
                INSERT INTO product(id,name,home,create_time,update_time,state) 
                value('%s','%s','%s','%s','%s')
                """
                self.cursor.execute(
                    sql % (pid, item['product'], item['product_home'], now, now, 1))
                self.connect.commit()
            self.cursor.execute(
                "UPDATE video SET screenshot = '%s',thumb = '%s',tags = '%s',create_date= '%s',update_time = '%s'" \
                ",pid = '%s' WHERE id = '%s'" % (item['screenshot'], item['thumb'], item['tags'], item['create_date'],
                                                 datetime.datetime.now(), pid, _id))
            self.connect.commit()
        elif item['create_date'] is None:
            self.cursor.execute("UPDATE video SET state = -1 WHERE id = '%s'" % _id)
            self.connect.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
