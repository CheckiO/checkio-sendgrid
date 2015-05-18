import json
import requests

from .exceptions import *
from .settings import *

__version__ = '1.0'


class Request(object):

    def send(self, method, url, **kwargs):
        return requests.request(method, url, **kwargs)

    def decode(self, response):
        raise NotImplementedError


class RequestJSON(Request):
    format = 'json'

    def decode(self, response):
        if response.status_code >= 500:
            raise ServerError()

        data = json.loads(response.content)
        if isinstance(data, dict) and data.get('message') == 'error':
            raise ServerError(data.get('errors'), data)
        return data


class RequestXML(Request):
    format = 'xml'


def request_builder(format):
    if format == RequestJSON.format:
        return RequestJSON()
    if format == RequestXML.format:
        return RequestXML()
    raise FormatNotAllowed("Format %s not allowed" % format)


class Sendgrid(object):
    """ Sendgrid API Wrapper """
    api_user = None
    api_key = None
    api_url_main = 'https://api.sendgrid.com/api/'
    timeout = DEFAULT_TIMEOUT

    request = None
    format = None

    def __init__(self, api_user, api_key, request_format='json', request_builder=request_builder):
        self.api_user = api_user
        self.api_key = api_key
        self.format = request_format
        self.request = request_builder(self.format)

    def _call(self, url, method='POST', data=None):
        """ Construct an API request, send it to the API, and parse the response. """
        auth_data = {
            'api_user': self.api_user,
            'api_key': self.api_key,
        }
        data.update(auth_data)

        headers = {
            'User-Agent': 'python-sendgrid/%s' % __version__,
            'Accept': 'application/%s' % self.format
        }
        data['headers'] = headers
        response = self.request.send(method, url, timeout=self.timeout, data=data)
        return self.request.decode(response)

    def list_add(self, list_name):
        url = '%snewsletter/lists/add.%s' % (self.api_url_main, self.format)
        return self._call(url, data=dict(list=list_name))

    def list_delete(self, list_name):
        url = '%snewsletter/lists/delete.%s' % (self.api_url_main, self.format)
        return self._call(url, data=dict(list=list_name))

    def email_add(self, list_name, email, name=None, custom_data=None):
        user_data = custom_data or {}
        user_data['email'] = email
        if name is not None:
            user_data['name'] = name
        users_data = (user_data,)
        return self.emails_add(list_name, users_data)

    def emails_add(self, list_name, users_data):
        url = '%snewsletter/lists/email/add.%s' % (self.api_url_main, self.format)

        inserted = 0
        for i in xrange(0, len(users_data), USER_ADD_LIMIT):
            users = users_data[i:i+USER_ADD_LIMIT]
            data = {
                'list': list_name,
                'data': map(json.dumps, users)
            }
            response = self._call(url, data=data)
            inserted += response.get('inserted')
        return inserted

    def email_delete(self, list_name, email):
        url = '%snewsletter/lists/email/delete.%s' % (self.api_url_main, self.format)
        data = {
            'list': list_name,
            'email': email
        }
        response = self._call(url, data=data)
        return response.get('removed')

    def unsubscribes_get(self, email=None):
        url = '%sunsubscribes.get.%s' % (self.api_url_main, self.format)
        data = {}
        if email is not None:
            data = {
                'email': email
            }
        response = self._call(url, data=data)
        return response
