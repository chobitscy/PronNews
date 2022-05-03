import datetime
import json
from copy import deepcopy
from functools import reduce

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin
from PronNews.utils import figure_from_str


class FCR_1Spider(RedisSpider, DataMixin):
    name = 'FCR_1'
    allowed_domains = ['adult.contents.fc2.com']
    base_url = 'https://adult.contents.fc2.com/article/%s/review'
    redis_key = name
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCR.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT id,vid FROM video WHERE state = 3"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        vid = item['vid']
        yield scrapy.Request(self.base_url % vid, callback=self.parse, meta={'target': item}, dont_filter=True)

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
