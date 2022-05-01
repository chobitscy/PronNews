import datetime
from copy import deepcopy
from functools import reduce

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import figure_from_str


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
        sql = "SELECT id,vid FROM video WHERE create_time BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND NOW()" \
              " AND state = 1"
        super().custom(sql)

    def start_requests(self):
        for result in self.results:
            vid = result['vid']
            yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'target': result})

    def parse(self, response, **kwargs):
        try:
            target = response.meta['target']
            soup = BeautifulSoup(response.text, 'lxml')
            selector = soup.select('.items_comment_headerReviewInArea li > span')
            rate_list = reversed([int(n.get_text()) for n in selector])
            comments = sum(deepcopy(rate_list))
            rate_list = [rate * index for index, rate in enumerate(rate_list, 1)]
            rate = reduce(lambda x, y: x + y, rate_list) if len(rate_list) != 0 else 0
            likes = figure_from_str(soup.select('.items_comment_headerInfo li:nth-child(1)')[0].get_text())
            info = Video()
            info['id'] = target['id']
            info['vid'] = target['vid']
            info['rate'] = rate
            info['comments'] = comments
            info['likes'] = likes
            info['update_time'] = datetime.datetime.now()
            yield info
        except IndexError:
            pass

    def close(self, spider, reason):
        super().flushall()
