import datetime
import json
import re

import scrapy
from bs4 import BeautifulSoup
from dateutil.parser import parse

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import size_to_MIB, schedule


class FCASpider(scrapy.Spider, DataMixin):
    name = 'FCA'
    allowed_domains = ['adult.contents.fc2.com'],
    redis_key = name
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FC2.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT id,vid FROM todo LIMIT 1000"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        vid = item['vid']
        yield scrapy.Request('https://sukebei.nyaa.si/user/offkab?f=2&c=0_0&q=' + vid, callback=self.parse,
                             meta={'target': item})

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        item = soup.select('tbody tr')
        info = Video()
        if len(item) == 0:
            sql = "DELETE FROM todo WHERE vid = %s" % response.meta['target']['vid']
            super().operation(sql)
            return
        item = item[0]
        pub_date = parse(item.select('.text-center:nth-child(5)')[0].get_text())
        pub_date = pub_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        title = item.select('td:nth-child(2) a')[0].get_text()
        vid = re.findall('FC2-PPV-(.*?) ', title)[0]
        info_hash = item.select('.fa-magnet')[0].parent.get('href')[20:60]
        speeders = int(item.select('.text-center:nth-child(6)')[0].get_text())
        downloads = int(item.select('.text-center:nth-child(7)')[0].get_text())
        completed = int(item.select('.text-center:nth-child(8)')[0].get_text())
        size = size_to_MIB(item.select('.text-center:nth-child(4)')[0].get_text())
        info['vid'] = vid
        info['title'] = title
        info['pub_date'] = pub_date
        info['info_hash'] = info_hash
        info['size'] = size
        info['speeders'] = speeders
        info['downloads'] = downloads
        info['completed'] = completed
        yield info

    def close(self, spider, reason):
        task_list = [
            {'project': 'PN', 'spider': 'FCD'},
            {'project': 'PN', 'spider': 'FCR'},
            {'project': 'PN', 'spider': 'JT'}
        ]
        schedule(task_list)
