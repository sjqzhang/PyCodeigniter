#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class CI_Mail(object):
    def __init__(self,**kwargs):
        self.host=kwargs['host'];
        self.user=kwargs['user'];
        self.password=kwargs['password'];
        self.postfix=kwargs['postfix'];



    def send(self,to,subject,content,attachs=[]):
        msg=MIMEMultipart('related')
        if isinstance(to,basestring):
            to=[to]
        if isinstance(attachs,basestring):
            attachs=[attachs]
        me=self.user+"<"+self.user+"@"+self.postfix+">"
        tmsg = MIMEText(content,_subtype='html',_charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = ";".join(to)
        msg.attach(tmsg)
        if len(attachs)>0:
            for file_name in attachs:
                if os.path.exists(file_name):
                    att = MIMEText(open('%s'%file_name, 'rb').read(), 'base64', 'utf-8')#添加附件
                    att["Content-Type"] = 'application/octet-stream'
                    att["Content-Disposition"] = 'attachment; filename="%s"'% os.path.basename(file_name)
                    msg.attach(att)
                else:
                    self.app.logger.warn('attach fail '+file_name+' not exist!')
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

    conf={
        'host':'smtp.163.com',
        'user':'abc',
        'password':'abc',
        'postfix':'163.com'
}
    mail=CI_Mail(**conf)
    mail.send('abc@163.com','你好','<h1>你为</h1>asdfasdfasf',[r'c:/test.txt'])


