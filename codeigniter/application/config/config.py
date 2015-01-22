
import logging


db={
    'host':'127.0.0.1',
    'user':'root',
    'passwd':'root',
    'database':'test',
    'maxconnections':30,
    'blocking':True,
}



log={

    'log_file':r'./log.log',
    'log_level':logging.INFO

}


mail={
    'host':'smtp.163.com',
    'user':'abc',
    'password':'abc',
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

