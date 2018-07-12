# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class Company(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    _id = Field()
    companyId = Field()
    englishName = Field()
    chineseName = Field()
    companyTyper = Field()
    establishDate = Field()
    companyStatus = Field()
    Remarks = Field()


class ProxyCookiesMap(scrapy.Item):
    _id = Field()
    proxy = Field()
    cookies = Field()
    is_valid = Field()
    last_raise_time = Field()
    failed_times = Field()
