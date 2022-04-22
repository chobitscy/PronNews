import json

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.JT import jav_torrent
from PronNews.mixin.dateMixin import DataMixin


class JT(scrapy.Spider, DataMixin):
    name = 'JT'
    allowed_domains = ['jav-torrent.org']
    base_url = 'https://jav-torrent.org/search?keyword=%s'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.JT.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        sql = "SELECT vid FROM video WHERE pub_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW()"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'vid': vid})

    def parse(self, response, **kwargs):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        selector = soup.select('.show-image')[0].get('data-image')
        item = jav_torrent()
        item['vid'] = meta['vid']
        item['print_screen'] = ','.join([n['src'] for n in json.loads(selector)])
        yield item
