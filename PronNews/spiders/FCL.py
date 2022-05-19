import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.todo import Todo
from PronNews.mixin.dateMixin import DataMixin


class FCLSpider(RedisSpider, DataMixin):
    name = 'FCL'
    redis_key = 'product_info_FCL'
    allowed_domains = ['adult.contents.fc2.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCL.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def make_requests_from_url(self, item):
        item = json.loads(item)
        home = item['home']
        if home.find('https://adult.contents.fc2.com/users/') == -1:
            return
        page = 1
        yield scrapy.Request(home + '/articles?sort=date&order=desc&deal=&page=%d' % page, callback=self.parse,
                             meta={'target': item, 'page': page})

    def parse(self, response, **kwargs):
        target = response.meta['target']
        page = response.meta['page'] + 1
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            articles = [re.findall(r'id=(\d+)', n.get('href'))[0] for n in
                        soup.select('.c-cntCard-110-f_itemName')]
            if len(articles) != 0:
                info = Todo()
                info['id'] = target['pid']
                info['vid'] = articles
                yield info
                url = target['home'] + '/articles?sort=date&order=desc&deal=&page=%d' % page
                yield scrapy.Request(url, callback=self.parse, meta={'target': target, 'page': page})
        except IndexError:
            pass
