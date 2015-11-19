#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

from codeigniter import CI_Application

from codeigniter import ci

def main():
    app=CI_Application(r'./')
    app.start_server()

if __name__ == '__main__':
    main()
