#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

__all__=['reactor']

if __name__=='__main__':
    pass
else:
    pass
    # #print("---"+__name__+"---")
    # import os,re
    # # ctrls= os.listdir(os.getcwd()+'/system/core')
    # ctrls= os.listdir( os.path.dirname(__file__) )
    # for c in ctrls:
    #         __all__.append(os.path.basename(c).split('.')[0])


import StringIO,traceback
def PushTraceback():
    fstring = StringIO.StringIO()
    traceback.print_exc(file=fstring)
    message = fstring.getvalue()
    print message
    return message

