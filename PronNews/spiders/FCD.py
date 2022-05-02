import datetime
import json

import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from PronNews.items.video import Video
from PronNews.mixin.dateMixin import DataMixin


class FCDSpider(RedisSpider, DataMixin):
    name = 'FCD'
    allowed_domains = ['adult.contents.fc2.com']
    base_url = 'https://adult.contents.fc2.com/article/%s/'
    redis_key = 'FCD'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FCD.Pipeline': 500,
        },
        'EXTENSIONS': {
            'PronNews.extends.closed.CloseSpiderRedis': 500
        },
        'CLOSE_SPIDER_AFTER_IDLE_TIMES': 1
    }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        sql = "SELECT id,vid FROM video WHERE create_date is NOT NULL AND state = 1 LIMIT 10"
        super().custom(sql)
        super().push(self.redis_key, self.results)

    def make_requests_from_url(self, item):
        item = json.loads(item)
        yield scrapy.Request(self.base_url % item['vid'], callback=self.parse, meta={'target': item})

    def parse(self, response, **kwargs):
        target = response.meta['target']
        soup = BeautifulSoup(response.text, 'lxml')
        screenshot_list = soup.select('.items_article_SampleImagesArea img')
        screenshot = ','.join([n.get('src')[35:] for n in screenshot_list]) if len(screenshot_list) != 0 else ''
        thumb_ele = soup.select('.items_article_MainitemThumb img')
        thumb = thumb_ele[0].get('src') if len(thumb_ele) > 0 else None
        tags = ','.join([n.get_text() for n in soup.select('.tagTag')])
        create_date_ele = soup.select('.items_article_Releasedate p')
        create_date = create_date_ele[0].get_text().split(':')[1].strip() if len(create_date_ele) > 0 else None
        product_ele = soup.select('.items_article_StarA+ li a')
        if len(product_ele) != 0:
            product, product_home = product_ele[0].get_text(), product_ele[0].get('href')
        else:
            product, product_home = None, None
        info = Video()
        info['id'] = target['id']
        info['vid'] = target['vid']
        info['screenshot'] = screenshot
        info['thumb'] = thumb
        info['product'] = product
        info['product_home'] = product_home
        info['tid'] = tags
        info['create_date'] = create_date
        info['update_time'] = datetime.datetime.now()
        print(info)
