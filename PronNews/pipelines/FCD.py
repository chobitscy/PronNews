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

        product_list = set([n['product'] for n in self.items])

        pid_list = self.session.query(Product).filter(
            Product.name.in_(product_list)).with_entities(Product.name, Product.id).all()

        pid_list = [(pn.decode('utf-8'), pd) for pn, pd in pid_list]

        # name -> pid
        name_with_pid = dict(pid_list)

        for item in self.items:
            if item['create_date'] is not None:
                product = item['product']
                if product in list(name_with_pid.keys()):
                    pid = name_with_pid[product]
                else:
                    pd = Product(item['product'], item['product_home'], None)
                    pid = pd.id
                    self.session.add(pd)
                    self.session.commit()
                item['pid'] = pid
            else:
                item['pid'] = None
                item['state'] = -1

        self.session.bulk_update_mappings(Video, self.items)
        self.session.commit()
        self.session.close()
