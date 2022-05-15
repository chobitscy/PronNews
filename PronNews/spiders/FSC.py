import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin


class FSC(RedisSpider, DataMixin):
    name = 'FSC'
    base_url = 'https://sukebei.nyaa.si/view/%s'
    redis_key = name
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FSC.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        sql = "SELECT id,vid,cid FROM video WHERE print_screen IS NULL AND state = 1" \
              " AND pub_date BETWEEN DATE_SUB(NOW(),INTERVAL 1 DAY) AND NOW()"
        super().custom(sql)
        super().push(self.redis_key, self.results, cid=True)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        cid = item['cid']
        yield scrapy.Request(self.base_url % cid, callback=self.parse, meta={'target': item})

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        selector = soup.select('#torrent-description')[0].get_text().split('\n')
        for text in selector:
            if text != '' and len(re.findall(r'https://(.*?)_s.jpg.html', text)) != 0:
                domain = re.findall(r'https://(.*?)/', text)[0]
                _id = re.findall(r'https://%s/(.*?)/' % domain, text)[0]
                data = {
                    'op': 'view',
                    'id': str(_id),
                    'pre': '1',
                    'next': 'Continue to image...'
                }
                yield scrapy.FormRequest(text, callback=self.parse_real, formdata=data, meta=response.meta)

    def parse_real(self, response):
        target = response.meta['target']
        item = Video()
        item['id'] = target['id']
        item['vid'] = target['vid']
        try:
            src = re.findall(r'<img src="(.*?)" class="pic"', response.text)[0]
            item['print_screen'] = src
        except IndexError:
            item['print_screen'] = None
        yield item
