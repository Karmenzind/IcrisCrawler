# -*- coding: utf-8 -*-
# Define here the models for your spider middleware

import random
import time
from collections import defaultdict
from urllib.parse import urljoin

import requests
from scrapy import Request, exceptions, signals
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware
# from scrapy.downloadermiddlewares import cookies
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import NotConfigured
from scrapy.http.cookies import CookieJar
from scrapy.utils.httpobj import urlparse_cached
from six.moves.urllib.request import proxy_bypass

from IcrisCrawler.db import proxy_cookies_collection
from IcrisCrawler.utils import new_request, ts_after_some_sec


class IcriscrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.

        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.

        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).

        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IcriscrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IpCookieMap:
    collection = proxy_cookies_collection
    login_url = ('https://www.icris.cr.gov.hk/csci/login_i.do'
                 '?loginType=iguest'
                 '&CHKBOX_01=false'
                 '&OPT_01=1'
                 '&OPT_02=0'
                 '&OPT_03=0'
                 '&OPT_04=0'
                 '&OPT_05=0'
                 '&OPT_06=0'
                 '&OPT_07=0'
                 '&CHKBOX_08=false'
                 '&OPT_08=1'
                 '&CHKBOX_09=false'
                 '&OPT_09=1'
                 '&username=iguest'
                 )

    def process_request(self, request, spider):
        if '_ignore_me' in request.meta:
            return

        proxy = request.meta.get('proxy')

        if not proxy:
            return
        is_stored, available_cookies = self.get_stored(proxy)

        if is_stored:
            if available_cookies:
                spider.logger.debug(
                    'Applied stored cookies for proxy %s' % proxy)
                request.cookies = available_cookies
            else:
                return new_request(request)
        else:
            return self.login_request(proxy, request, spider)

    def store_proxy(self, proxy):
        _ = {'proxy': 'proxy'}
        proxy_cookies_collection.update_one(_, {'$set': {}}, upsert=True)

    def get_stored(self, proxy):
        """

        :param proxy:
        :return: is_stored, available_cookies
        """
        spec = dict(proxy=proxy)
        found_one = self.collection.find_one(spec)
        is_stored = bool(found_one)
        available_cookies = None

        if found_one and time.time() - found_one.get('last_raise_time', 0) > 120:
            available_cookies = found_one.get('cookies')

        return is_stored, available_cookies

    def login_request(self, proxy, request, spider):
        meta = {
            'proxy': proxy,
            'max_retry_times': 3,
            'download_timeout': 10,
            '_ignore_me': None,
            '_deferred_request': new_request(request),
        }

        return Request(self.login_url,
                       callback=spider.parse_login,
                       meta=meta,
                       priority=1000,
                       )

    def save_cookies(self, proxy, cookies):
        _filter = {'proxy': proxy}
        _update = {"$set": {'cookies': cookies}}
        self.collection.update_one(_filter, _update, upsert=True)


class LocalProxyCookies:

    def process_request(self, request, spider):
        proxy, cookies = self.get_proxy_and_cookies()
        request.cookies = cookies
        request.meta['proxy'] = proxy
        spider.logger.debug(
            'Applied proxy:%s and cookies: %s' % (proxy, cookies))

    def get_proxy_and_cookies(self):
        from IcrisCrawler.db import proxy_cookies_collection
        _f = {
            'is_valid': True,
            '$or': [
                {'last_raise_time': {'$lt': time.time() - 120}},
                {'last_raise_time': {'$exists': False}},
            ]
        }
        docs = proxy_cookies_collection.find(_f)

        if docs:
            found_one = random.choice(list(docs))

            return found_one.get('proxy'), found_one.get('cookies')
        else:
            raise exceptions.IgnoreRequest('No available cookies')


class FPServerMiddleware(HttpProxyMiddleware):
    """
    A middleware, based on FPServer, continuesly fetch random proxy
    and set it for each request.
    FPServer required.

    required config items: (Must/Optional)
        FP_SERVER_URL               M
        HTTPPROXY_AUTH_ENCODING     O   default: latin-l
        FP_SERVER_PROXY_ANONYMITY   O   default: random
            choices:    `transparent` `anonymous`
    """

    def __init__(self,
                 crawler,
                 auth_encoding,
                 fps_url,
                 anonymity):

        if not fps_url:
            raise NotConfigured('FP_SERVER_URL not configured')

        self.fps_api = urljoin(fps_url, '/api/proxy/')

        self.anonymity = anonymity

        self.logger = crawler.spider.logger
        self.crawler = crawler
        self.auth_encoding = auth_encoding

    def fetch_proxy(self, scheme):
        """
        Get proxy from fpserver by given scheme.

        :scheme: `str` proxy protocol
        :return:
            url, scheme
        """

        params = {
            "scheme": scheme,
            "anonymity": self.anonymity,
        }
        text = None
        try:
            req = requests.get(self.fps_api, params=params)
            text = req.text
            data = req.json()
        except:
            self.crawler.logger.exception(
                "Failed to fetch proxy: %s" % text)
        else:
            _code = data.get('code')
            _proxies = data.get('data', {}).get('detail', [])

            if (_code is not 0) or (not _proxies):
                self.logger.warning(
                    'Response of fetch_proxy: %s' % data)

                return
            proxy_info = _proxies[0]
            proxy_url = proxy_info['url']

            return self._get_proxy(proxy_url, scheme)

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING',
                                             'latin-l')
        fps_url = crawler.settings.get('FP_SERVER_URL')
        anonymity = crawler.settings.get('FP_SERVER_PROXY_ANONYMITY')

        return cls(crawler, auth_encoding, fps_url, anonymity)

    def _set_proxy(self, request, scheme):
        _fetched = self.fetch_proxy(scheme)

        if not _fetched:
            self.logger.debug('No proxy fetched from fp-server.')

            return

        creds, proxy = _fetched
        request.meta['proxy'] = proxy
        self.logger.debug('Applied proxy: %s' % proxy)

        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds

    def process_request(self, request, spider):
        # ignore if proxy is already set

        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return

            # extract credentials if present
            creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url

            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds

            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes

        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return

        self._set_proxy(request, scheme)


class MultiProxyCookies(CookiesMiddleware):
    """
    use proxy as cookiejarkey
    """

    def __init__(self, debug=False, concurrent_proxies=None):
        self.jars = defaultdict(CookieJar)
        self.debug = debug
        self.sleep_until = dict()
        self.black_list_proxies = set()
        self.failure_counter = defaultdict(int)
        self.concurrent_proxies = concurrent_proxies

    def choice_existed_cookiejarkey(self):
        _l = list(self.jars.keys())

        return random.choice(_l)

    def process_request(self, request, spider):
        if request.meta.get('dont_merge_cookies', False):
            return

        cookiejarkey = request.meta.get("proxy")

        action = request.meta.get('_action')
        c_id = request.meta.get('_c_id')
        info = '(%s: %s)' % (action, c_id)

        # no proxy
        if random.random() <= 0.3 and self.sleep_until.get(None, 0) < time.time():
            if not (action == 'consult' and None not in self.jars):
                spider.logger.debug('%s Use local ip for this request.' % info)
                cookiejarkey = request.meta['proxy'] = None

        if cookiejarkey in self.black_list_proxies:
            spider.logger.debug(
                '%s %s is blacklisted. Rescheduling……' % (info, cookiejarkey))

            return spider.login_request(c_id)

        # if available cookies > 100
        # use existed cookies
        if len(self.jars) - len(self.sleep_until) > self.concurrent_proxies:
            cookiejarkey = self.choice_existed_cookiejarkey()
            spider.logger.debug(
                '%s Reused existed cookiejarkey %s' % (info, cookiejarkey))
            request.meta['proxy'] = cookiejarkey

        if cookiejarkey in self.jars:
            if cookiejarkey in self.sleep_until:
                if time.time() < self.sleep_until.get(cookiejarkey, 0):
                    # reschedule login
                    # without proxy
                    spider.logger.debug(
                        '%s %s need to sleep. Rescheduling……' % (info, cookiejarkey))

                    return spider.login_request(c_id)
                else:
                    self.sleep_until.pop(cookiejarkey, None)

            if action == 'login':
                # rescheduling consult request
                # with proxy
                spider.logger.debug(
                    '%s Found cookie for %s. Rescheduling……' % (info, cookiejarkey))

                return spider.consult_request(c_id, proxy=cookiejarkey, priority=2)

        jar = self.jars[cookiejarkey]
        cookies = self._get_request_cookies(jar, request)

        for cookie in cookies:
            jar.set_cookie_if_ok(cookie, request)

        # set Cookie header
        request.headers.pop('Cookie', None)
        jar.add_cookie_header(request)
        self._debug_cookie(request, spider)

    def process_response(self, request, response, spider):
        cookiejarkey = request.meta.get("proxy")
        c_id = request.meta.get('_c_id')
        action = request.meta.get('_action')

        if response.status == 302:
            self.reset_cookiejarkey(cookiejarkey, spider)

            return spider.login_request(c_id)

        t = response.text

        if action == 'consult':
            if '如要继续查阅公司资料, 请输入上图的验证密码' in t or 'Please enter the VERIFICATION' in t:
                self.sleep_until[cookiejarkey] = ts_after_some_sec(120)

                return spider.login_request(c_id)

        if request.meta.get('dont_merge_cookies', False):
            return response

        # extract cookies from Set-Cookie and drop invalid/expired cookies
        jar = self.jars[cookiejarkey]
        jar.extract_cookies(response, request)
        self._debug_set_cookie(response, spider)

        return response

    def process_exception(self, request, exception, spider):
        c_id = request.meta.get('_c_id')
        cookiejarkey = request.meta.get('proxy')
        spider.logger.warning("Failed at %s with proxy %s. Rescheduling…… (%s)"
                              % (c_id, cookiejarkey, exception))

        def _ban_condition():
            yield isinstance(exception, TunnelError)
            yield isinstance(exception, ConnectionRefusedError)
            yield self.failure_counter[cookiejarkey] >= 5

        # banned
        if cookiejarkey and any(_ban_condition()):
            self.ban_cookiejarkey(cookiejarkey, spider)
        else:
            self.failure_counter[cookiejarkey] += 1
            self.sleep_until[cookiejarkey] = ts_after_some_sec(5)

        return spider.login_request(c_id)

    def ban_cookiejarkey(self, cookiejarkey, spider):
        self.black_list_proxies.add(cookiejarkey)

        for s in (self.jars, self.sleep_until, self.failure_counter):
            s.pop(cookiejarkey, None)

        spider.logger.debug('Banned %s. Blacklist length: %s'
                            % (cookiejarkey, len(self.black_list_proxies)))

    def reset_cookiejarkey(self, cookiejarkey, spider):
        """
        # reset but not banned

        :param cookiejarkey:
        :param spider:
        :return:
        """

        for s in (self.jars, self.sleep_until):
            s.pop(cookiejarkey, None)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('COOKIES_ENABLED'):
            raise NotConfigured

        return cls(
            crawler.settings.getbool('COOKIES_DEBUG'),
            crawler.settings.get('CONCURRENT_PROXIES', 500),
        )
