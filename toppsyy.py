import time

import requests
import simplejson as json

API_HOST = 'http://otter.topsy.com'
API_KEY = 'GET YOUR OWN :)'
DEFAULT_PERPAGE = 100

try:
    from local_settings import API_KEY
except:
    pass


class Result(object):
    
    def __init__(self, request):
        self._request = request
        self._data = json.loads(request.content)
        self.request = self._data['request']
        self.response = self._data['response']
        for k in self.response.keys():
            setattr(self, k, self.response[k])


class Topsy(object):
    
    def __init__(self, api_key=''):
        self._api_key = api_key or API_KEY
        self._api_host = API_HOST
        self._rate_limit = 0
        self._rate_limit_remaining = 0
        self._rate_limit_reset = 0

    def _get(self, resource='', **params):
        params['apikey'] = self._api_key
        url = '%s/%s.json' % (self._api_host, resource)
        r = requests.get(url, params=params)
        self._rate_limit = r.headers['x-ratelimit-limit']
        self._rate_limit_remaining = r.headers['x-ratelimit-remaining']
        self._rate_limit_reset = r.headers['x-ratelimit-reset']
        return Result(request=r)

    def more(self, result):
        '''return the next page of results, if possible, or nothing''' 
        if len(result.list) < int(result.request['parameters']['perpage']):
            return None
        resource = result.request['resource']
        params = result.request['parameters']
        params['page'] = int(params.get('page', 1)) + 1
        params['offset'] = result.response['last_offset']
        return self._get(resource, **params)

    @property
    def remaining(self):
        return int(self._rate_limit_remaining)

    @property
    def reset(self):
        '''how many hours until the rate_limit_remaining resets?'''
        diff_secs = int(self._rate_limit_reset) - int(time.time())
        diff_hours = diff_secs / (60 * 60.0)
        return diff_hours

    def authorinfo(self, nick=''):
        url = 'http://twitter.com/%s' % nick
        return self._get('authorinfo', url=url)

    def experts(self, query='', **params):
        return self._get('experts', q=query, **params)

    def populartrackbacks(self, url):
        return self._get('populartrackbacks', url=url)

    def linkposts(self, nick='', contains='', tracktype=''):
        url = 'http://twitter.com/%s' % nick
        return self._get('linkposts', url=url, contains=contains,
            tracktype=tracktype)

    def linkpostcount(self, nick='', contains='', tracktype=''):
        url = 'http://twitter.com/%s' % nick
        return self._get('linkpostcount', url=url, contains=contains,
            tracktype=tracktype)

    def search(self, q='', **params):
        return self._get('search', q=q, perpage=DEFAULT_PERPAGE,
                **params)

    def searchcount(self, q='', dynamic=''):
        return self._get('searchcount', q=q, dynamic=dynamic)

    def searchhistogram(self, q='', slice='86400', period='30', 
        count_method='target'):
        return self._get('searchhistogram', q=q, slice=slice,
            period=period, count_method=count_method)

    def searchdate(self, q='', window='', type='', zoom=10):
        return self._get('search', q=q, window=window, type=type,
            zoom=zoom)

    def stats(self, url='', contains=''):
        return self._get('stats', url=url, contains=contains)

    def top(self, thresh='top100', type='', locale=''):
        if thresh not in ['top100', 'top1k', 'top5k', 'top20k']:
            thresh = 'top100'
        if type not in ['', 'image', 'video', 'tweet']:
            type = ''
        if locale not in ['', 'en', 'ja', 'ko', 'de', 'pt', 'es', 'th', 'fr']:
            locale = ''
        return self._get('top', thresh=thresh, type=type, locale=locale)

    def trackbacks(self, url='', contains='', ifonly='', sort_method=''):
        return self._get('trackbacks', url=url, contains=contains,
            ifonly=ifonly, sort_method=sort_method)

    def urlinfo(self, url=''):
        return self._get('urlinfo', url=url)
