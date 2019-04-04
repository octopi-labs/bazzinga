
import sys
from socket import timeout

from libapp.dovesoft.version import __version__

from .exceptions import DoveSoftClientError, DoveSoftServerError

try:
    import urllib.request as urllib_request
    from urllib.parse import urlencode
    from urllib.error import HTTPError
except ImportError:  # Python 2
    import urllib2 as urllib_request
    from urllib2 import HTTPError
    from urllib import urlencode



class DoveSoftClient(object):
    """ DoveSoft API """

    def __init__(self, username, password_or_key=None, **kwargs):
        """
        Construct DoveSoft API object
        """
        self.useragent = 'dovesoft/' + __version__ + ';python'
        self.username = username
        self.password = password_or_key
        self.host = kwargs.get('host', "http://mobicomm.dove-sms.com")
        self.endpoint = kwargs.get('endpoint', "/submitsms.jsp")
        self.sms_url = "{host}{endpoint}".format(host=self.host, endpoint=self.endpoint)
        self._raise_errors = kwargs.get('raise_errors', False)
        # urllib cannot connect to SSL servers using proxies
        self.proxies = kwargs.get('proxies', None)

    def _build_body(self, message):
        if sys.version_info < (3, 0):
            ks = ["senderid", "accusage", "smstype"]
            for k in ks:
                v = getattr(message, k)
                if isinstance(v, unicode):
                    setattr(message, k, v.encode('utf-8'))

        values = {
            'mobile': message.mobile,
            'message': message.message,
            'senderid': message.senderid,
            'accusage': message.accusage,
            'unicode': message.unicode_status,
            'smstype': message.smstype,
            'time': message.time,
            'idno': message.idno
        }

        if self.username != None:
            # Using username + password
            values['user'] = self.username
            values['key'] = self.password

        for k in list(values.keys()):
            if not values[k]:
                del values[k]
        return values

    def _make_request(self, message):
        if self.proxies:
            proxy_support = urllib_request.ProxyHandler(self.proxies)
            opener = urllib_request.build_opener(proxy_support)
            urllib_request.install_opener(opener)
        data = urlencode(self._build_body(message), True).encode('utf-8')
        req = urllib_request.Request("{url}?{data}".format(url=self.sms_url, data=data))
        response = urllib_request.urlopen(req, timeout=10)
        body = response.read()

        return response.getcode(), body

    def send(self, message):
        if self._raise_errors:
            return self._raising_send(message)
        else:
            return self._legacy_send(message)

    def _legacy_send(self, message):
        try:
            return self._make_request(message)
        except HTTPError as e:
            return e.code, e.read()
        except timeout as e:
            return 408, e

    def _raising_send(self, message):
        try:
            return self._make_request(message)
        except HTTPError as e:
            if 400 <= e.code < 500:
                raise DoveSoftClientError(e.code, e.read())
            elif 500 <= e.code < 600:
                raise DoveSoftServerError(e.code, e.read())
            else:
                assert False
        except timeout as e:
            raise DoveSoftClientError(408, 'Request timeout')
