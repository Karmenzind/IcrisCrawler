# coding: utf-8
import pymongo


def _get_mongo_cli():
    from IcrisCrawler import settings
    _conf = getattr(settings, 'MONGODB_CONFIG', {})
    return pymongo.MongoClient(**_conf)


def _init_index():
    """
    create indexes
    :return:
    """
    q1 = proxy_cookies_collection.create_index('proxy', unique=True)
    q2 = company_collection.create_index('companyId', unique=True)
    print(q1, q2)


mongo_cli = _get_mongo_cli()
db = mongo_cli.icris

proxy_cookies_collection = db.proxy_cookies
company_collection = db.company

_init_index()
