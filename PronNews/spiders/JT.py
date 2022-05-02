import datetime
import json

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin


class JT(RedisSpider, DataMixin):
    name = 'JT'
    allowed_domains = ['jav-torrent.org']
    base_url = 'https://jav-torrent.org/search?keyword=%s'
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
        sql = "SELECT id,vid FROM video WHERE print_screen IS NULL WHERE state = 1"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        vid = item['vid']
        yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'target': item})

    def parse(self, response, **kwargs):
        target = response.meta['target']
        item = Video()
        item['id'] = target['id']
        item['vid'] = target['vid']
        item['update_time'] = datetime.datetime.now()
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            selector = soup.select('.show-image')[0].get('data-image')
            item['print_screen'] = ','.join([n['src'] for n in json.loads(selector)])
        except IndexError:
            item['state'] = -1
        yield item
