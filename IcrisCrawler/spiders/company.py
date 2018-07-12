# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from scrapy import FormRequest, Request
from scrapy.spiders import CrawlSpider

from IcrisCrawler.db import company_collection
from IcrisCrawler.items import Company
from IcrisCrawler.utils import (
    get_payload,
    request_failed,
    login_url,
    consult_url
)


class CompanySpider(CrawlSpider):
    name = 'company'
    allowed_domains = ['icris.cr.gov.hk']

    handle_httpstatus_list = [302]

    custom_settings = dict(
        # HTTPCACHE_ENABLED=False,
        DOWNLOAD_DELAY=0,
        RETRY_ENABLED=False,
        # Enable and configure the AutoThrottle extension (disabled by default)
        # See https://doc.scrapy.org/en/latest/topics/autothrottle.html
        AUTOTHROTTLE_ENABLED=True,
        # The initial download delay
        AUTOTHROTTLE_START_DELAY=1,
        # The maximum download delay to be set in case of high latencies
        AUTOTHROTTLE_MAX_DELAY=3,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        # AUTOTHROTTLE_TARGET_CONCURRENCY=1.0,
        # Enable showing throttling stats for every response received:
        # AUTOTHROTTLE_DEBUG = False
        DOWNLOADER_MIDDLEWARES={
            'IcrisCrawler.middlewares.FPServerMiddleware': 300,
            'IcrisCrawler.middlewares.MultiProxyCookies': 301,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        },
        # DEPTH_PRIORITY=1,
        # SCHEDULER_DISK_QUEUE='scrapy.squeues.PickleFifoDiskQueue',
        # SCHEDULER_MEMORY_QUEUE='scrapy.squeues.FifoMemoryQueue',
    )

    def login_request(self, c_id, proxy=None, priority=0):
        """

        :param c_id:
        :param proxy:
        :return:
        """
        meta = {
            '_action': 'login',
            '_c_id': c_id,
            'download_timeout': 20,
            'max_retry_times': 1,
        }
        if proxy:
            meta['proxy'] = proxy

        return Request(login_url,
                       dont_filter=True,
                       callback=self.after_login,
                       meta=meta,
                       priority=priority,
                       )

    def consult_request(self, c_id, proxy, priority=0):
        data = get_payload(c_id)

        meta = {
            '_action': 'consult',
            '_c_id': c_id,
            'download_timeout': 30,
            'max_retry_times': 0,
            'proxy': proxy,
        }

        return FormRequest(consult_url,
                           method='POST',
                           formdata=data,
                           dont_filter=True,
                           callback=self.parse_item,
                           # errback=request_failed,
                           priority=priority,
                           meta=meta,
                           )

    def start_requests(self):
        for c_id in self.get_code_range():
            yield self.login_request(c_id)

    def parse_item(self, response):
        c_id = response.meta['_c_id']
        data = {}
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            companys = soup.select('.data')
            names = companys[3].text.strip().split('\r')
            data = Company({
                'companyId': companys[1].text.strip(),
                'englishName': names[0],
                'chineseName': names[1] if len(names) > 1 else None,
                'companyTyper': companys[5].text.strip(),
                'establishDate': companys[7].text.strip(),
                'companyStatus': companys[9].text.strip(),
                'Remarks': companys[11].text.strip()
            })
        except:
            self.logger.exception('failed at company %s' % c_id)

        return data

    def get_code_range(self):
        """
        :return: iterator
        """

        if self.settings.get('IS_TEST'):
            c_id = self.settings.get('TEST_CODE')

            return [c_id]
        else:
            s = self.settings.get('START_CODE')
            e = self.settings.get('END_CODE')

            def _r():
                for c_id in range(s, e):
                    _filter = dict(companyId=str(c_id))

                    if company_collection.find_one(_filter):
                        self.logger.debug('%s has been crawled. Ignored.' % c_id)
                    else:
                        yield c_id

            return _r()

    def after_login(self, response):
        c_id = response.meta['_c_id']
        proxy = response.meta['proxy']
        yield self.consult_request(c_id, proxy)
