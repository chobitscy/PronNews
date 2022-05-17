import datetime
import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin


class FCN(RedisSpider, DataMixin):
    name = 'FCN'
    redis_key = name
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCN.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT id,vid FROM video WHERE cid IS NULL"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        vid = item['vid']
        yield scrapy.Request('https://sukebei.nyaa.si/user/offkab?f=2&c=0_0&q=' + vid, callback=self.parse,
                             meta={'target': item})

    def parse(self, response, **kwargs):
        target = response.meta['target']
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            item = soup.select('tbody tr')[0]
            info = Video()
            info['id'] = target['id']
            info['update_time'] = datetime.datetime.now()
            title_ele = item.select('td:nth-child(2) a')
            if len(title_ele) == 1:
                url = title_ele[0].get('href')
            else:
                url = title_ele[1].get('href')
            info['cid'] = re.findall(r'/view/(\d+)', url)[0]
            yield info
        except IndexError:
            pass
