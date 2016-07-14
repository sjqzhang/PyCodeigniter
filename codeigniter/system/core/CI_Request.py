#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import sys

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
        self.method = env["REQUEST_METHOD"]
        self.query_params = {}
        self.query_string = env["QUERY_STRING"]
        self.path = env["PATH_INFO"]
        self.post_params = {}
        self.params={}
        self.env_raw = env

        for param, value in parse_qs(env["QUERY_STRING"]).items():
            self.query_params[param] = value[0]

        if (self.method == "POST"
            and env["CONTENT_TYPE"] == "application/x-www-form-urlencoded"):
            self.post_params = {}
            content = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
            post_params = parse_qs(content)

            for param, value in post_params.items():
                decoded_param = param.decode('utf-8')
                decoded_value = value[0].decode('utf-8')
                self.post_params[decoded_param] = decoded_value

        self.params=dict(self.query_params.items()+ self.post_params.items())

    def get_param(self, name, default=None):
        """
        Returns a param of a GET request identified by its name.
        """
        try:
            return self.params[name]
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
            return self.env_raw[wsgi_header]
        except KeyError:
            return default