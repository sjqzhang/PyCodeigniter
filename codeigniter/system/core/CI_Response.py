#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

HTTP_CODES = {200: "200 OK",
              301: "301 Moved Permanently",
              302: "302 Found",
              400: "400 Bad Request",
              401: "401 Unauthorized",
              500: "500 Internal Error",
              404: "404 Not Found"}



class CI_Response(object):
    def __init__(self):
        self.headers = []
        self.cookies = {}
        self.status =HTTP_CODES[200]
        self.body=""

    def set_header(self,key,value):
        if type(key) == str and type(value):
            self.headers.append( (key,value) )

    def set_status_code(self,code):
        if code in HTTP_CODES.keys():
            self.status= HTTP_CODES[code]
        else:
            raise  Exception('Status Code Not Found')












if __name__=='__main__':
    rep=CI_Response()



    print(rep.status)


