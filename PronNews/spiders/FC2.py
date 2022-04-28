import datetime
import re
import time

import requests
import scrapy
from bs4 import BeautifulSoup
from dateutil.parser import parse

from PronNews import settings
from PronNews.items.nyaa import Nyaa
from PronNews.utils import schedule


class Fc2Spider(scrapy.Spider):
    name = 'FC2'
    allowed_domains = ['sukebei.nyaa.si']
    base_site = 'https://sukebei.nyaa.si/?q=FC2&c=0_0&f=0&u=offkab&p=%d'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.nyaa.Pipeline': 500,
        }
    }
    page_no = 1

    def start_requests(self):
        yield scrapy.Request(self.base_site % self.page_no, self.parse)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.select('tbody tr')
        count = 0
        for item in items:
            pub_date = parse(item.select('.text-center:nth-child(5)')[0].get_text())
            pub_date = pub_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
            if pub_date.timestamp() > time.mktime((datetime.date.today() + datetime.timedelta(weeks=-1)).timetuple()):
                title = item.select('td:nth-child(2) a')[0].get_text()
                vid = re.findall('FC2-PPV-(.*?) ', title)[0]
                info_hash = item.select('.fa-magnet')[0].parent.get('href')[20:60]
                speeders = int(item.select('.text-center:nth-child(6)')[0].get_text())
                downloads = int(item.select('.text-center:nth-child(7)')[0].get_text())
                completed = int(item.select('.text-center:nth-child(8)')[0].get_text())
                size = self.size_to_MIB(item.select('.text-center:nth-child(4)')[0].get_text())
                info = Nyaa()
                info['vid'] = vid
                info['title'] = title
                info['pub_date'] = pub_date
                info['info_hash'] = info_hash
                info['size'] = size
                info['speeders'] = speeders
                info['downloads'] = downloads
                info['completed'] = completed
                count += 1
                yield info
        if len(items) == count:
            self.page_no += 1
            yield scrapy.Request(self.base_site % self.page_no, self.parse)

    @staticmethod
    def size_to_MIB(size: str):
        number = float(re.findall(r"\d+\.?\d*", size)[0])
        if size.find('GiB') != -1:
            return number * 1024
        elif size.find('MiB') != -1:
            return number

    def close(self, spider, reason):
        task_list = [
            {'project': 'PN', 'spider': 'JT'},
            {'project': 'PN', 'spider': 'FCR'},
            {'project': 'PN', 'spider': 'FCD'}
        ]
        schedule(task_list)
