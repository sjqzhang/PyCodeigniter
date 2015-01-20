
import logging


db={
    'host':'172.16.132.230',
    'user':'root',
    'passwd':'root',
    'database':'test',
    'maxconnections':3,
    'blocking':True,
}

log={

    'log_file':r'/log/abc.log',
    'log_level':logging.INFO

}

config={

'log':log,
'db':db

}


if __name__=='__main__':
    print(config)

