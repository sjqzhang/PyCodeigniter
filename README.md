##1.Install

###1.1 dependency
+ `logging`
+ `pymysql`
+ `DBUtils`
+ `apscheduler`

###1.2 how to install
```

wget --no-check-certificate https://raw.githubusercontent.com/sjqzhang/PyCodeigniter/master/install.sh -O- |sh

or

git clone https://github.com/sjqzhang/PyCodeigniter.git

pip install -r requirements.txt

python setup.py install


```


##2. How to use?


####2.1 simple example (integrate with fastpy http server)


```python

#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'
from codeigniter.system.core.CI_Application import CI_Application

def main():
    app=CI_Application(r'./')

    app.server.start()

if __name__ == '__main__':
    main()


```


command line

```
python app.py
```

visit website

```
http://127.0.0.1:8005/Index/index

```

####2.2 how to integrate with `web.py`

```python
#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import web

from codeigniter.system.core.CI_Application import CI_Application


ci=CI_Application(application_path=r'./')


urls = (
    '/.*', ci.router.webpy_route
)
app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore('sessions'))


if __name__ == "__main__":


    app.run()
```


####2.3 how to integrate with `gevent`

```python

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

def application(env, start_response):
    html=''

    code,obj=ci.router.wsgi_route(env)
    if not isinstance(obj,str) and not isinstance(obj,unicode):
        html=json.dumps(obj)
        start_response(str(code), [('Content-Type', 'application/json')])
    else:
        start_response(str(code), [('Content-Type', 'text/html')] )
        if isinstance(obj,unicode):
            html=unicode.encode(obj,'utf-8')
        else:
            html=obj
    return [str(html)]



if __name__ == "__main__":
    print 'Serving on %s...' % port
    WSGIServer((host, port), application).serve_forever()




```




##3. Q&A
+ how to user pycodeigniter in your application?

```

step 1: create instace

from codeigniter.system.core.CI_Application import CI_Application

app=CI_Application(application_path=r'./')




step 2: import singleton ci 

from codeigniter import ci


```





+ how to config your application?

```
#you can edit application/config/config.py

config.py

```


+ how to visit your website?

```

#http://127.0.0.1:8005/conntroller_class/function
#


http://127.0.0.1:8005/Index/index



```


+ how to get controller class instance?

```
ci.loader.ctrl('classname')

```


+ how to get model class instance?

```
ci.loader.model('classname')

```

+ how to operate database?


```
#you can use active record.

ci.db.ar().select('*').table('test').limit(10).get()

ci.db.query('select * from test')

ci.db.insert('test',{'name':'test'})

ci.db.delete('test',{'id':'5'})

ci.db.update('test',{'name':'test'},{'id':'5'})


```

+ how to write log in your application ?

```
ci.logger.info('message')

ci.logger.warn('message')

ci.logger.error('message')

```

+ how to send email?

```

#send mail with attachment
ci.mail.send('to','subject','message',['/tmp/sendfile'])



```


+ how to set timer?

```
ci.cron.add_cron('*/1 * * * * *','class.method')
for exmaple
ci.cron.add_cron('*/1 * * * * *','Index.acc')

```


+ how to cache result?

```
	description:


    ttl:expire (second)
    prefix:group
    key:key

    @CI_Cache.Cache(prefix='abc',ttl=3,key='#p[0]')
    def abc(self,id="0"):
        return "test cache"


```


+ how to cache result in redis or other cache container?

```


## cache must be impliment function "put" "get" "delete"
## function prototype as bellow

class B(object):
    def __init__(self):
        self._cache=redis.StrictRedis('172.16.3.92')

    def put(self,key,value,ttl=3600):
        self._cache.setex(key,ttl,value)

    def get(self,key,ttl):
        self._cache.get(key)

#how to use
ci.cache.set_cache(B())

```


## how to use zookeeper (is_leader) ?

```
while True:
    if ci.zk.is_leader():
        pass
    else:
        pass
```


## how to get zookeeper instance (kazoo) ?
```
 zk=ci.zk.get_zk()
 
```

