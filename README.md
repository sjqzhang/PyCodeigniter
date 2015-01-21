##1.dependency

+ `logging`
+ `pymysql`
+ `DBUtils`


##2. How to use?

```python
#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



import os
import sys

def app_run(system_path,application_path):
    sys.path.insert(0,application_path)
    sys.path.insert(0,system_path+os.path.sep+'core')
    exec(r'from CI_Application import CI_Application')
    app=CI_Application(system_path,application_path)
    return app

def start_server(app):
    httpd=make_server(app.config['server']['host'],app.config['server']['port'],app.request_hander)
    httpd.serve_forever()

if __name__=='__main__':
    app=app_run('./system','./application')
    #app=app_run('path/to/system','path/to/your/application')
    start_server(app)
    
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
app.loader.ctrl('classname')

```


+ how to get model class instance?

```
app.loader.model('classname')

```

+ how to operate database?


```
#you can use active record.

app.db.query('select * from test')

app.db.insert('test',{'name':'test'})

```

+ how to write log in your application ?

```
app.logger.info('message')

app.logger.warn('message')

app.logger.error('message')

```

+ how to send email?

```

#send html
app.mail.send('to','subject','message',true)

#send text
app.mail.send('to','subject','message',false)


```