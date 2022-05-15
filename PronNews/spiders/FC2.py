import datetime
import re
import time

import scrapy
from bs4 import BeautifulSoup
from dateutil.parser import parse

from PronNews.items.video import Video
from PronNews.utils import schedule, size_to_MIB


class Fc2Spider(scrapy.Spider):
    name = 'FC2'
    allowed_domains = ['sukebei.nyaa.si']
    base_site = 'https://sukebei.nyaa.si/?q=FC2&c=0_0&f=0&u=offkab&p=%d'
    custom_settings = {
        'ITEM_PIPELINES': {
            'PronNews.pipelines.FC2.Pipeline': 500,
        }
    }
    page_no = 1

    def start_requests(self):
        yield scrapy.Request(self.base_site % self.page_no, self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.select('tbody tr')
        count = 0
        for item in items:
            try:
                pub_date = parse(item.select('.text-center:nth-child(5)')[0].get_text())
                pub_date = pub_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
                if pub_date.timestamp() > time.mktime(
                        (datetime.date.today() + datetime.timedelta(weeks=-1)).timetuple()):
                    title_ele = item.select('td:nth-child(2) a')
                    if len(title_ele) == 1:
                        title = title_ele[0].get_text()
                        url = title_ele[0].get('href')
                    else:
                        title = title_ele[1].get_text()
                        url = title_ele[1].get('href')
                    vid = re.findall(r'FC2-PPV-(\d+) ', title)[0]
                    info_hash = item.select('.fa-magnet')[0].parent.get('href')[20:60]
                    speeders = int(item.select('.text-center:nth-child(6)')[0].get_text())
                    downloads = int(item.select('.text-center:nth-child(7)')[0].get_text())
                    completed = int(item.select('.text-center:nth-child(8)')[0].get_text())
                    size = size_to_MIB(item.select('.text-center:nth-child(4)')[0].get_text())
                    info = Video()
                    info['vid'] = vid
                    info['title'] = title
                    info['pub_date'] = pub_date
                    info['info_hash'] = info_hash
                    info['size'] = size
                    info['speeders'] = speeders
                    info['downloads'] = downloads
                    info['completed'] = completed
                    info['cid'] = re.findall(r'/view/(\d+)', url)[0]
                    count += 1
                    yield info
            except IndexError:
                continue
        if len(items) == count:
            self.page_no += 1
            yield scrapy.Request(self.base_site % self.page_no, self.parse)

    def close(self, spider, reason):
        task_list = [
            {'project': 'PN', 'spider': 'FCD'},
            {'project': 'PN', 'spider': 'FCR'},
            {'project': 'PN', 'spider': 'JT'}
        ]
        schedule(task_list, distribution=True)
