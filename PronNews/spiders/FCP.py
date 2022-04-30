import datetime

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.product import Product
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import figure_from_str


class FCRSpider(scrapy.Spider, DataMixin):
    name = 'FCP'
    allowed_domains = ['adult.contents.fc2.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCP.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = """
        SELECT * FROM product WHERE home IS NOT NULL 
            AND create_time BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW()
        """
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            home = result['home']
            if home.find('http') == -1:
                continue
            yield scrapy.Request(home, callback=self.parse, meta={'id': result['id']})

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
