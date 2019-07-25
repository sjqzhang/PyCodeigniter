
# Feature

1. Automatically generated  project structure

2. integrated logger mysql redis  memcache zookeeper email cron gevent  ...

3. everything is ready for you.(^_^)


##1.Install

###1.1 dependency
+ `logging`
+ `pymysql` or `MySQLdb`  (if you want to use mysql)
+ `gevent` (if you want to build  high performance )

```
optional
   redis
   memcache
   .....
```
###1.2 how to install
```

wget --no-check-certificate https://raw.githubusercontent.com/sjqzhang/PyCodeigniter/master/install.sh -O- |sh

or

git clone https://github.com/sjqzhang/PyCodeigniter.git

pip install -r requirements.txt

python setup.py install


```


##2. How to use?


####2.1 simple example


```python

#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'
from codeigniter.system.core.CI_Application import CI_Application

def main():
    app=CI_Application(r'./')

    app.start_server()

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

+ how to get config in your application?

```

  ci.config.get('your key')



```

Note: `your key must define in config dict`

for exmaple:
```
config={

'log':log,
'db':db,
'mail':mail,
'server':server,
'cache':cache,
'autoload':autoload,
}


ci.config.get('db')



```


+ how to visit your website?

```

#http://127.0.0.1:8005/conntroller_class/function
#


http://127.0.0.1:8005/Index/index



```

+ how to get request parameters?

```
ci.local.input.get('name')

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

ci.db.select('*')._from('test').limit(10).get()

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

    @CI_Cache.Cache(prefix='abc',ttl=3,key='#id')
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


容器如何使用

拉取容器
```
docker pull sjqzhang/pycodeigniter
```

在宿主机/data/pyapp/上创建app.py
```python
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

```
运行容器
```
docker run -d -p 8005:8005 -v /data/pyapp:/data/pyapp sjqzhang/pycodeigniter
```



# if yout want to know more , please see the test case!!


