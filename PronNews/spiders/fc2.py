from functools import reduce

import scrapy
from bs4 import BeautifulSoup

from PronNews.items.fc2 import Fc2
from PronNews.mixin.dateMixin import DataMixin


class Fc2Spider(scrapy.Spider, DataMixin):
    name = 'fc2'
    allowed_domains = ['adult.contents.fc2.com']
    base_url = 'https://adult.contents.fc2.com/article/%s/review'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.fc2.Pipeline': 500,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        super().last_week_vid()

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
        screenshot_list = soup.select('.items_comment_SampleImageArea img')
        rate = reduce(lambda x, y: x + y, rate_list) if len(rate_list) != 0 else 0
        screenshot = ','.join([n.get('src')[35:] for n in screenshot_list]) if len(screenshot_list) != 0 else ''
        thumb = soup.select('.items_comment_MainitemThumb img')[0].get('src')
        fc2 = Fc2()
        fc2['vid'] = meta['vid']
        fc2['rate'] = rate
        fc2['screenshot'] = screenshot
        fc2['thumb'] = thumb
        yield fc2
