
import logging



sdb={
    'type':'sqlite', #sqlite or mysql
    'host':'',
    'user':'',
    'passwd':'',
    'database':'test.db',
    'charset':'utf8',
    'maxconnections':30,
    'blocking':True,
    'autocommit':True,
    'debug':True
}


mdb={
    'type':'mysql',
    'host':'127.0.0.1',
    'user':'root',
    'passwd':'root',
    'database':'test',
    'charset':'utf8',
    'maxconnections':1,
    'blocking':True,
    'autocommit':True,
    'debug':True
}



log={

    'file':r'./log.log',
    'level':logging.INFO,
    'file_size':1024*1024*100,
    'back_count':10

}



log2={
    'file':r'./log2.log',
    'level':logging.INFO,
    'file_size':1024*1024*100,
    'back_count':10

}


log3={
    'file':r'./log3.log',
    'level':logging.INFO,
    'file_size':1024*1024*100,
    'back_count':10
}

mail={
    'host':'abc.abc.com',
    'user':'abc',
    'password':'123456',
    'postfix':'abc.com'
}


server={
    'port':8006,
    'host':'0.0.0.0',
    'envroment':'development',
    'static_dir':'static',
    'cache_dir':'cache',
    'access_log_dir':'logs'
}


cache={
    # 'type':'redis',
    #   'type':'memcache',
    'type':'memory',
    'cache_instance':'',
    'max_count':100
}


autoload={
    'controllers':{
        #"Index":"Index",
        #'Test':'tpl'
    },
    'models':{
       # 'test_model':'TestModel',
       # "Test":"Test"

    },
    'library':{


    },
    'helps':{

    }

}

memcache={
     'servers':['172.16.3.92:11211'],
}


cron={
 'threadpool':20,
 'processpool':5,
 'jobs':[
     {'cron':'0/5 * * * * *','command':'Index.task'}
 ]
}

template={
    'path':"./views",
    # 'engine':'Tenjin'
     'engine':'jinja2'
}


zookeeper={
    'url':'172.16.10.66:2181,172.16.10.163:2181,172.16.10.96:2181',
    'password':'',
    'user':'',
    'path':'/tmp',
    'timeout':10

}

redis={
'host':'172.16.3.92',
# 'port':6379,
'db':3,
# 'password':None,
'max_connections':10
}


session = {
    'type':'local',## redis|local
    'expire':86400,
    # 'host': "127.0.0.1:6379",
    # 'passwd':""
}



config={

'log':log,
'db':sdb,
'mdb':mdb,
'mail':mail,
'server':server,
'cache':cache,
'autoload':autoload,
'template':template,
'log2':log2,
'log3':log3,
'redis':redis,
'memcache':memcache,
# 'session':session
# 'cron':cron,
#'zookeeper':zookeeper,
# 'use_threads':True

}


if __name__=='__main__':
    print(config)

