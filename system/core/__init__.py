#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

__all__=[]

if __name__=='__main__':
    pass
else:
    #print("---"+__name__+"---")
    import os,re
    ctrls= os.listdir(os.getcwd()+'/system/core')
    for c in ctrls:
            __all__.append(os.path.basename(c).split('.')[0])
