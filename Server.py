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

import cgi
import os

from urllib import unquote
import urlparse 

def download(env, start_response):
    try:
        code="200 OK"
        data={}
        if len(urlparse.parse_qsl(env['QUERY_STRING']))==0:
            start_response( code, [('Content-Type', 'html/text')])
            return "(error) -f(filename) require" 
	for i in urlparse.parse_qsl(env['QUERY_STRING']):
            data[i[0]]=i[1]

        filename= data['file'] #env['QUERY_STRING'].split('=')[1]
	filename=unquote(filename)
	filename=filename.replace('+',' ')
	print filename
        directory= data['dir']
        directory=directory.replace('.','')
        filepath='files/'+directory+'/'+filename
        if not os.path.isfile(filepath):
            start_response( '404 Not Found', [('Content-Type', 'html/text')])
            return "(error) file not found" 
        the_file=open(filepath,'rb')
        size=os.path.getsize(filepath)
        response_headers = [ ('Content-Type', 'application/octet-stream'), ('Content-length', str(size)) ]
        start_response( code, response_headers )
        return iter(lambda: the_file.read(1024), '')

    except:
        pass



def application(env, start_response):
    html=''


    path=env['PATH_INFO']

    if path.find('download')>0:
        return download(env,start_response)


    code,obj=ci.router.wsgi_route(env)
    #print type(obj)
    if not isinstance(obj,str) and not isinstance(obj,unicode):
        html=json.dumps(obj)
        start_response(str(code), [('Content-Type', 'application/json')])
    else:
	try:
            html=unicode(obj).encode('utf-8')
	except:
	    html=obj
        start_response(str(code), [('Content-Type', 'text/html')])
    return [str(html)]



if __name__ == "__main__":
    print 'Serving on %s...' % port
    WSGIServer((host, port), application).serve_forever()
# app.loader.ctrl("Index").add("ls -alh ")




