import time

from scrapy.http.cookies import CookieJar

from IcrisCrawler.db import proxy_cookies_collection

consult_url = 'https://www.icris.cr.gov.hk/csci/cps_criteria.do'
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

def new_request(request):
    """
    without old proxy
    """
    new = request.copy()
    new.meta.pop('proxy', None)

    return new


def update_raise_time(proxy):
    _filter = dict(proxy=proxy)
    _update = {
        '$set': {
            'last_raise_time': time.time(),
        }
    }
    q = proxy_cookies_collection.update_one(_filter, _update)

    return extract_mongodb_result(q, _filter, _update)


def extract_mongodb_result(query, _filter=None, _update=None):
    msg = 'matched_count: %s modified_count: %s ' % (
        getattr(query, 'matched_count', 'UNKNOWN'),
        getattr(query, 'modified_count', 'UNKNOWN'),
    )

    if _filter:
        msg += 'filter: %s ' % _filter

    if _update:
        msg += 'update: %s ' % _update

    return msg


def get_cookies_dict_from_response(response):
    jar = CookieJar()
    jar.extract_cookies(response, response.request)
    cookie_objs = jar.make_cookies(response, response.request)
    cookies = {_.name: _.value for _ in cookie_objs}

    return cookies


def request_failed(failure):
    """
    failurefor scrapy.Request's errback
    to handle http error
    """
    proxy = failure.request.meta.get('proxy')
    _f = dict(proxy=proxy)
    _u = {'$inc': {'failed_times': 1}}
    doc_after = proxy_cookies_collection.find_one_and_update(
        _f, _u, return_document=True)

    if doc_after.get('failed_times') >= 3:
        _u = {'$set': {'is_valid': False}}
        proxy_cookies_collection.find_one_and_update(_f, _u)


def reset_proxy(proxy):
    _f = dict(proxy=proxy)
    _u = {'$unset': {'is_valid': ''}}
    doc_after = proxy_cookies_collection.find_one_and_update(
        _f, _u, return_document=True, upsert=True)
    return doc_after

def get_payload(x):
    data = {
        'CRNo': str(x),
        'DPDSInd': 'true',
        'companyName': '',
        'language': 'en',
        'mode': 'EXACT NAME',
        'nextAction': 'cps_criteria',
        'page': '1',
        'radioButton': 'BYCRNO',
        'searchMode': 'BYCRNO',
        'searchPage': 'True',
        'showMedium': 'true',
    }

    return data


def parse_302(response):
    """

    :param response:
    :return: new request for
    """
    proxy = response.request.meta.get('proxy')
    if 'Please select the type of login' in response.text:
        reset_proxy(proxy)
    return new_request(response.request)


def ts_after_some_sec(secs=1):
    return time.time() + secs
