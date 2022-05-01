import datetime
import json

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.video import Video
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
        sql = "SELECT id,vid FROM video WHERE print_screen IS NULL"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'target': result})

    def parse(self, response, **kwargs):
        try:
            target = response.meta['target']
            soup = BeautifulSoup(response.text, 'lxml')
            selector = soup.select('.show-image')[0].get('data-image')
            item = Video()
            item['id'] = target['id']
            item['vid'] = target['vid']
            item['print_screen'] = ','.join([n['src'] for n in json.loads(selector)])
            item['update_time'] = datetime.datetime.now()
            yield item
        except IndexError:
            pass
