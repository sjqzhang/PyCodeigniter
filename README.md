
# Feature

1. Automatically generated  project structure

2. integrated logger mysql redis  memcache zookeeper email cron gevent  ...

3. everything is ready for you.(^_^)


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



# exmaple

```python

#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import CI_Cache

class Index:


    def index(self,req,resp):
        return "hello world"

    def favicon(self,req,resp):
        return "favicon"

    def test_task(self,req,resp):
        import datetime
        print('timer:'+ str(datetime.datetime.now()))

    def test_db(self,req,resp):
        row= ci.db.query('select 1')
        print(ci.db.scalar('select 1'))
        # ci.db.insert('tablenname',{'fieldname1':'value1','fieldname2':'value2'})
        # ci.db.update('tablenname',{'fieldname1':'value1','fieldname2':'value2'},{'condition':'conditionvalue'})
        # ci.db.select('*')._from('test').limit(10).get()
        return row

    def test_config(self,req,resp):
        print(ci.config)

    def test_loader(self,req,resp):
        ci.loader.helper('your helper')
        ci.loader.library('your library')
        ci.loader.model('your model')




    #how to create different instance ?
    def test_loader_instances(self,req,resp):
        #how to connect to different db ?

        db2=ci.loader.cls('CI_DB')(ci.config['db2']) # how to create different db instance and save it into ci
        ci.set('db2',db2)  # save it  into ci
        print(ci.get('db2').query('select 1'))

        #how to log to different file ?

        logger2=ci.loader.cls('CI_Logger')(ci.config['log2']) # how to create different db instance and save it into ci
        ci.set('logger2',logger2)  # save it  into ci
        print(ci.get('logger2').info('asdfasdfas'))

        #The rest may be deduced by analogy


    def test_mail(self,req,resp):
        ci.mail.send(['test@abc.com'],'test','message')

    @CI_Cache.Cache(prefix='test_auto_cache',ttl=3600,key='#id,#name')
    def test_auto_cache(self,id=0,name='hello'): #auto cache result
        ci.cacche.set('abc',"hello world")
        return ci.cache.get('abc')
    def test_cache(self,req,resp):
        ci.cacche.set('abc',"hello world")
        return ci.cache.get('abc')

    def test_logger(self,req,resp):
        ci.logger.info('Hello World')

    def test_redis(self,req,resp):
        self.redis.set('test','test') # see redis api
        return self.redis.get('test')

    def test_memcache(self,req,resp):
        self.memcache.set('test','test') # see memcache api
        return self.memcache.get('test')

    def test_tpl(self,req,resp): #template
        return ci.tpl.render('template.html',[{'sNo':'123456','chinese':67,'math':90,'englist':85},\
            {'sNo':'123456','chinese':80,'math':96,'englist':85}])










```