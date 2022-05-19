import datetime
import json

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.product import Product
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import figure_from_str


class FCRSpider(RedisSpider, DataMixin):
    name = 'FCP'
    redis_key = 'product_info_FCP'
    allowed_domains = ['adult.contents.fc2.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCP.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def make_requests_from_url(self, item):
        item = json.loads(item)
        home = item['home']
        if home.find('http') == -1:
            return
        yield scrapy.Request(home, callback=self.parse, meta={'id': item['pid']})

    def parse(self, response, **kwargs):
        try:
            meta = response.meta
            soup = BeautifulSoup(response.text, 'lxml')
            avatar = soup.select('.seller_user_accountIcon img')[0].get('src')
            works = soup.select('.seller_user_accountInfo span:nth-child(1)')[0].get_text()
            works = figure_from_str(works)
            fans = soup.select('.seller_user_accountInfo span:nth-child(2)')[0].get_text()
            fans = figure_from_str(fans)
            info = Product()
            info['id'] = meta['id']
            info['avatar'] = avatar
            info['works'] = works
            info['fans'] = fans
            info['update_time'] = datetime.datetime.now()
            yield info
        except IndexError:
            pass
