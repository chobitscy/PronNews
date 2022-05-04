import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.mixin.dateMixin import DataMixin
from PronNews.items.video import Video

import datetime
import json


class JAP(RedisSpider, DataMixin):
    name = 'JAP'
    allowed_domains = ['javpop.com']
    base_url = 'http://javpop.com/index.php?s=%s'
    redis_key = name
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.JT.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        sql = "SELECT id,vid FROM video WHERE print_screen IS NULL AND state = 1"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        vid = item['vid']
        yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'target': item})

    def parse(self, response, **kwargs):
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            selector = soup.select('#content .thumb_post li a')[0].get('href')
            yield scrapy.Request(selector, callback=self.parse_content, meta={'target': response.meta['target']})
        except IndexError:
            pass

    def parse_content(self, response):
        try:
            target = response.meta['target']
            soup = BeautifulSoup(response.text, 'lxml')
            selector = [n.get('src') for n in soup.select('.screenshot img')]
            info = Video()
            info['id'] = target['id']
            info['print_screen'] = ','.join(selector)
            info['update_time'] = datetime.datetime.now()
            yield info
        except IndexError:
            pass
