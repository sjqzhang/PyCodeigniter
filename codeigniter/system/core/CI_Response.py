#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import sys
import datetime
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    import Cookie as cookies
if PY3:
    from http import cookies

SimpleCookie=cookies.SimpleCookie
CookieError=cookies.CookieError

HTTP_CODES = {200: "200 OK",
              301: "301 Moved Permanently",
              302: "302 Found",
              400: "400 Bad Request",
              401: "401 Unauthorized",
              500: "500 Internal Error",
              404: "404 Not Found"}

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

def is_ascii_encodable(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    except UnicodeDecodeError:

        return False
    except AttributeError:
        return False
    return True

class TimezoneGMT(datetime.tzinfo):
    GMT_ZERO = datetime.timedelta(hours=0)
    def utcoffset(self, dt):
        return self.GMT_ZERO
    def tzname(self, dt):
        return 'GMT'
    def dst(self, dt):
        return self.GMT_ZERO


class CI_Response(object):
    def __init__(self):
        self.headers = []
        self.cookies = {}
        self._status =HTTP_CODES[200]
        self.status=HTTP_CODES[200]
        self.body=""

    def set_header(self,key,value):
        if type(key) == str and type(value):
            self.headers.append( (key,value) )





    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,status=HTTP_CODES[200]):
        if str(status).isdigit() and status in HTTP_CODES.keys():
            self.status=HTTP_CODES[status]
        else:
            self._status=status


    def set_cookie(self, name, value, expires=None, max_age=None,
                   domain=None, path=None, secure=True, http_only=True):


        if not is_ascii_encodable(name):
            raise KeyError('"name" is not ascii encodable')
        if not is_ascii_encodable(value):
            raise ValueError('"value" is not ascii encodable')

        if PY2:
            name = str(name)
            value = str(value)

        if self.cookies is None:
            self.cookies = SimpleCookie()

        try:
            self.cookies[name] = value
        except CookieError as e:  # pragma: no cover

            raise KeyError(str(e))

        if expires:

            fmt = '%a, %d %b %Y %H:%M:%S GMT'
            if expires.tzinfo is None:
                # naive
                self.cookies[name]['expires'] = expires.strftime(fmt)
            else:
                # aware
                gmt_expires = expires.astimezone(TimezoneGMT())
                self.cookies[name]['expires'] = gmt_expires.strftime(fmt)

        if max_age:

            self.cookies[name]['max-age'] = int(max_age)

        if domain:
            self.cookies[name]['domain'] = domain

        if path:
            self.cookies[name]['path'] = path

        if secure:
            self.cookies[name]['secure'] = secure

        if http_only:
            self.cookies[name]['httponly'] = http_only