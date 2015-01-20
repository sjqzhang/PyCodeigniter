
import logging


db={
    'host':'172.16.132.230',
    'user':'root',
    'passwd':'root',
    'database':'test',
    'maxconnections':30,
    'blocking':True,
}



log={

    'log_file':r'/log/abc.log',
    'log_level':logging.INFO

}


mail={
    'host':'smtp.163.com',
    'user':'easyphp',
    'password':'123456',
    'postfix':'163.com'
}


server={
    'port':8005,
    'host':'0.0.0.0'
}

config={

'log':log,
'db':db,
'mail':mail,
'server':server

}


if __name__=='__main__':
    print(config)

