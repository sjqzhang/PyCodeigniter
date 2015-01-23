#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import smtplib
from email.mime.text import MIMEText



class CI_Mail(object):
    def __init__(self,**kwargs):
        self.host=kwargs['host'];
        self.user=kwargs['user'];
        self.password=kwargs['password'];
        self.postfix=kwargs['postfix'];



    def send(self,to,subject,content,is_html=True):
        if isinstance(to,basestring):
            to=[to]
        me=self.user+"<"+self.user+"@"+self.postfix+">"
        if is_html:
            msg = MIMEText(content,_subtype='html',_charset='utf-8')
        else:
            msg=content
        msg['Subject'] = subject
        msg['From'] = me

        msg['To'] = ";".join(to)
        try:
            s = smtplib.SMTP()
            s.connect(self.host)
            s.login(self.user,self.password)
            s.sendmail(me, to, msg.as_string())
            s.close()
            return True
        except Exception as  err:
            self.app.logger.error(err)
            return False

if __name__ == '__main__':
    pass