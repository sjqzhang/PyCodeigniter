#!/usr/bin/python
"""A web.py application powered by gevent"""

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
import time
import json

from codeigniter.system.core.CI_Application import CI_Application

ci=CI_Application(application_path=r'./')
port=ci.config['server']['port']
host=ci.config['server']['host']


if __name__ == "__main__":
    print 'Serving on %s...' % port
    WSGIServer((host, port), ci.application).serve_forever()