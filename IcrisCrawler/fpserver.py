from IcrisCrawler import settings
import requests

from urllib.parse import urljoin

fps_api = urljoin(settings.FP_SERVER_URL, '/api/proxy/')
anonymity = settings.FP_SERVER_PROXY_ANONYMITY


def fetch_proxy(scheme, count):
    """
    Get proxy from fpserver by given scheme.

    :scheme: `str` proxy protocol
    :return:
        urls
    """

    params = {
        "scheme": scheme,
        "anonymity": anonymity,
        "count": count,
    }
    text = None
    try:
        req = requests.get(fps_api, params=params)
        text = req.text
        data = req.json()
    except:
        print("Failed to fetch proxy: %s" % text)
    else:
        _code = data.get('code')
        _proxies = data.get('data', {}).get('detail', [])

        if (_code is not 0) or (not _proxies):
            print('Response of fetch_proxy: %s' % data)

            return

        for _p in _proxies:
            if _p.get('url'):
                yield _p.get('url')
