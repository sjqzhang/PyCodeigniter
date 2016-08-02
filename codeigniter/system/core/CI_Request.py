#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    from io import StringIO
    from http import cookies
if PY2:
    import StringIO
    import Cookie as cookies

import cgi
SimpleCookie = cookies.SimpleCookie

if sys.version_info >= (3, 0):
    from urllib.parse import parse_qs # pragma: no cover
    from urllib.parse import urlencode # pragma: no cover
    from urllib.parse import quote # pragma: no cover
else:
    from urlparse import parse_qs # pragma: no cover
    from urllib import urlencode # pragma: no cover
    from urllib import quote # pragma: no cover



class CI_Request(object):
    """
    Contains data of the current HTTP request.
    """
    def __init__(self, env):
        """
        :param env: Wsgi environment
        """
        self._has_parse=False
        self._method = env["REQUEST_METHOD"]
        self.query_params = {}
        self.query_string = env["QUERY_STRING"]
        self.path = env["PATH_INFO"]
        self.post_params = {}
        self._params={}
        self.env = env
        # self.stream = env['wsgi.input']
        self._cookies=None

        for param, value in parse_qs(env["QUERY_STRING"]).items():
            self.query_params[param] = value[0]

        self.parse_data()

        # if (self._method == "POST"
        #     and env["CONTENT_TYPE"] == "application/x-www-form-urlencoded"):
        #     self.post_params = {}
        #     content = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
        #     post_params = parse_qs(content)
        #     for param, value in post_params.items():
        #         decoded_param = param.decode('utf-8')
        #         decoded_value = value[0].decode('utf-8')
        #         self.post_params[decoded_param] = decoded_value

        self._params.update(self.query_params)
        # self._params.update(self.post_params)


    def parse_data(self):
        env=self.env
        if not self._has_parse and env['REQUEST_METHOD'] in ['POST', 'PUT']:
            if env.get('CONTENT_TYPE', '').lower().startswith('multipart/'):
                fp = env['wsgi.input']
                a = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=1)
            else:
                fdata=env.get('wsgi.input').read()
                try:
                    fp = StringIO(fdata)
                    a = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=1)
                except Exception as e:
                    data=parse_qs(fdata,keep_blank_values=1)
                    for key in data.keys():
                        self._params[ key ]=data[key][0]
                    return
        else:
            a = cgi.FieldStorage(environ=env, keep_blank_values=1)
        self._has_parse=True
        if not a.list is None :
            for key in a.keys():
                self._params[ key ] = a[key].value
        elif a.file :
            try:
                self._params[0]= a.file.read()
            except:
                pass

    @property
    def method(self):
        return self._method
    @property
    def content_length(self):
        try:
            value = self.env['CONTENT_LENGTH']
            if value.isdigit():
                return int(value)
        except KeyError:
            return None

    @property
    def params(self):
        return self._params
    @property
    def remote_addr(self):
        return self.env.get('REMOTE_ADDR')
    @property
    def cookies(self):
        if self._cookies is None:
            parser = SimpleCookie(self.get_header('Cookie'))
            cookies = {}
            for morsel in parser.values():
                cookies[morsel.key] = morsel.value

            self._cookies = cookies

        return self._cookies.copy()
    def get_param(self, name, default=None):
        """
        Returns a param of a GET request identified by its name.
        """
        try:
            return self._params[name]
        except KeyError:
            return default

    def post_param(self, name, default=None):
        """
        Returns a param of a POST request identified by its name.
        """
        try:
            return self.post_params[name]
        except KeyError:
            return default

    def header(self, name, default=None):
        """
        Returns the value of the HTTP header identified by `name`.
        """
        wsgi_header = "HTTP_{0}".format(name.upper())

        try:
            return self.env[wsgi_header]
        except KeyError:
            return default

    def get_header(self,name, default=None):
        return self.header(name,default)
