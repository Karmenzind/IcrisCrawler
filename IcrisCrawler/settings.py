# -*- coding: utf-8 -*-

# Scrapy settings for IcrisCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'IcrisCrawler'

SPIDER_MODULES = ['IcrisCrawler.spiders']
NEWSPIDER_MODULE = 'IcrisCrawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'IcrisCrawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    # 'Cookie': 'web.country=CN; web.language=zh; ROUTEID=.worker2; BIGipServerUXPWEB_443=208892426.47873.0000; JSESSIONID=b73PwJn8Jl2T2hqmMZmbV4hy0LGvFRp4MMTLGLTkWzrf0ZypJDGF!511399688',
    'Host': 'www.icris.cr.gov.hk',
    'Origin': 'https://www.icris.cr.gov.hk',
    'Referer': 'https://www.icris.cr.gov.hk/csci/cps_criteria.jsp',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'IcrisCrawler.middlewares.IcriscrawlerSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'IcrisCrawler.middlewares.IcriscrawlerDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'IcrisCrawler.pipelines.IcriscrawlerPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 30
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 120
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#######################################################################
#                               CUSTOM                                #
#######################################################################

# IS_TEST = True
TEST_CODE = 1769634  # tencent

START_CODE = 2267393
END_CODE = 3344095

# follow your real settings
FP_SERVER_URL = 'http://localhost:12345'
FP_SERVER_PROXY_ANONYMITY = 'anonymous'

STORED_COOKIES = 100

# for mongodb
MONGODB_CONFIG = {
    'host': '127.0.0.1',
    'port': 27017,
}

# concurrent proxies in MultiProxyCookies middleware
CONCURRENT_PROXIES = 500
