##1.dependency

+ `logging`
+ `pymysql`
+ `DBUtils`


##2. How to use?

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