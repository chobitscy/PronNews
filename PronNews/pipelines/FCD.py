import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from PronNews import settings
from PronNews.model.product import Product
from PronNews.model.video import Video


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
            Video.id, Video.vid, Video.create_date).all()

        pid_list = self.session.query(Product).filter(
            Product.name.in_([n['product'] for n in self.items])).with_entities(Product.name, Product.id).all()

        pid_list = [(pn.decode('utf-8'), pd) for pn, pd in pid_list]

        # name -> pid
        name_with_pid = dict(pid_list)

        # vid -> {id,cd}
        id_with_vd = {}
        for _id, vid, cd in targets:
            id_with_vd[vid] = {
                'id': _id,
                'cd': cd
            }

        for item in self.items:
            create_date = id_with_vd[item['vid']]['cd']
            item['id'] = id_with_vd[item['vid']]['id']
            item['update_time'] = datetime.datetime.now()
            if item['create_date'] is not None and create_date is None:
                product = item['product']
                if product in list(name_with_pid.keys()):
                    pid = name_with_pid[product]
                else:
                    pd = Product(item['product'], item['product_home'], None)
                    pid = pd.id
                    self.session.add(pd)
                    self.session.commit()
                item['pid'] = pid
            elif item['create_date'] is None:
                item['pid'] = None
                item['state'] = -1

        self.session.bulk_update_mappings(Video, self.items)
        self.session.commit()
        self.session.close()
