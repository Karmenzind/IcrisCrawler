# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import exceptions

from IcrisCrawler.db import company_collection, proxy_cookies_collection
from IcrisCrawler.items import Company, ProxyCookiesMap


class IcriscrawlerPipeline(object):

    def process_item(self, item, spider):
        if not item:
            raise exceptions.DropItem

        if isinstance(item, Company):
            c_id = item.get('companyId')

            if c_id is None:
                raise exceptions.DropItem
            _filter = dict(companyId=c_id)
            _update = {"$set": item}
            company_collection.update_one(_filter, _update, upsert=True)

        if isinstance(item, ProxyCookiesMap):
            proxy = item.get('proxy')
            _filter = dict(proxy=proxy)
            _update = {"$set": item}
            proxy_cookies_collection.update_one(_filter, _update, upsert=True)

        return item
