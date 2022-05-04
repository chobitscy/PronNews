import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
from PronNews.items.video import Video as VD
from PronNews.model.todo import Todo
from PronNews.model.video import Video
from PronNews.utils import get_snowflake_uuid


class Pipeline(object):

    def __init__(self):
        config = settings.MYSQL
        engine_config = 'mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8' % (
            config['user'], config['passwd'], config['host'], config['port'], config['db'])
        self.engine = create_engine(engine_config)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)

    def close_spider(self, spider):
        if len(self.items) == 0:
            return

        targets = self.session.query(Video).filter(Video.vid.in_([n['vid'] for n in self.items])).with_entities(
            Video.vid, Video.id).all()

        vid_with_id = dict(targets)

        update = []
        insert = []
        now = datetime.datetime.now()

        for item in self.items:
            if item['vid'] in list(vid_with_id.keys()):
                info = VD()
                info['speeders'] = item['speeders']
                info['downloads'] = item['downloads']
                info['completed'] = item['completed']
                info['id'] = vid_with_id[item['vid']]
                info['update_time'] = now
                update.append(info)
            else:
                item['id'] = get_snowflake_uuid()
                item['create_time'] = now
                item['update_time'] = now
                item['state'] = 1
                insert.append(item)

        self.session.bulk_update_mappings(Video, update)
        self.session.commit()

        self.session.bulk_insert_mappings(Video, insert)
        self.session.commit()

        self.session.close()
