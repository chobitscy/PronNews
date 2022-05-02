import re

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.todo import Todo
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import schedule


class FCLSpider(scrapy.Spider, DataMixin):
    name = 'FCL'
    allowed_domains = ['adult.contents.fc2.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCL.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT id,home FROM product WHERE home IS NOT NULL AND state = 1"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            home = result['home']
            if home.find('https://adult.contents.fc2.com/users/') == -1:
                continue
            page = 1
            yield scrapy.Request(home + '/articles?sort=date&order=desc&deal=&page=%d' % page, callback=self.parse,
                                 meta={'target': result, 'page': page})

    def parse(self, response, **kwargs):
        target = response.meta['target']
        page = response.meta['page'] + 1
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            articles = [re.findall(r'id=(\d+)', n.get('href'))[0] for n in
                        soup.select('.c-cntCard-110-f_itemName')]
            if len(articles) != 0:
                info = Todo()
                info['id'] = target['id']
                info['vid'] = articles
                yield info
                url = target['home'] + '/articles?sort=date&order=desc&deal=&page=%d' % page
                yield scrapy.Request(url, callback=self.parse, meta={'target': target, 'page': page})
        except IndexError:
            pass
