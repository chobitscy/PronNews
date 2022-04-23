from functools import reduce

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.nyaa import Nyaa
from PronNews.mixin.dateMixin import DataMixin


class FCRSpider(scrapy.Spider, DataMixin):
    name = 'FCR'
    allowed_domains = ['adult.contents.fc2.com']
    base_url = 'https://adult.contents.fc2.com/article/%s/review'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCR.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT vid FROM video WHERE pub_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW()" \
              " AND state = 1 AND type_id = 1"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'vid': vid})

    def parse(self, response, **kwargs):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        selector = soup.select('.items_comment_headerReviewInArea li > span')
        rate_list = reversed([int(n.get_text()) for n in selector])
        rate_list = [rate * index for index, rate in enumerate(rate_list, 1)]
        rate = reduce(lambda x, y: x + y, rate_list) if len(rate_list) != 0 else 0
        nyaa = Nyaa()
        nyaa['vid'] = meta['vid']
        nyaa['rate'] = rate
        yield nyaa
