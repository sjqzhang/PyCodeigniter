#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from hashlib import md5

import re
import os
import sys


class CI_Cron(object):
    def __init__(self,**kwargs):
        self._is_start=False
        self.jobs={}
        self.jobs_ids=[]
        self.config=kwargs['cron']
        self.app=kwargs['app']
        if 'threadpool' in self.config:
            threadpool=int(self.config['threadpool'])
        else:
            threadpool=20
        if 'processpool' in self.config:
            processpool=int(self.config['processpool'])
        else:
            processpool=5
        executors = {
            'default': ThreadPoolExecutor(threadpool),
            'processpool': ProcessPoolExecutor(processpool)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 60
        }
        scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        self.scheduler= scheduler


    def init(self):
        for cron in self.config['jobs']:
            if 'callback' in cron:
                self.add_cron(cron= cron['cron'],command=cron['command'],callback=cron['callback'])
            else:
                self.add_cron(cron= cron['cron'],command=cron['command'])
        self.scheduler.start()

    def execute(self,command='',callback=None):
        try:
            result=os.popen(command).read()
            if callback!=None:
                callback(result)
        except Exception as error:
            pass

    def _md5(self,s):
        m=md5()
        m.update(s)
        return m.hexdigest()


    def start(self):
        if not self._is_start:
            self._is_start=True
            self.scheduler.start()

    def add_cron(self,cron='',command='',callback=None,*args,**kwargs):
        try:
            _id=self._md5(str(cron)+str(command)+str(callback)+str(kwargs))
            for ids in self.jobs_ids:
                if _id==ids['md5']:
                    self.resume(ids['id'])
                    return ids['id']
            ts=re.split(r'\s+',cron)
            if callback!=None:
                callback=self._get_func(callback)
                kwargs['callback']=callback
            if isinstance(command,str) and command.startswith('script:'):
                kwargs['command']=command.replace('script:','')
                job=self.scheduler.add_job(self.execute,CronTrigger(second=ts[0],minute=ts[1],hour=ts[2],day=ts[3],month=ts[4],day_of_week=ts[5]),args=args,kwargs=kwargs)
            else:
                command=self._get_func(command)
                job=self.scheduler.add_job(command,CronTrigger(second=ts[0],minute=ts[1],hour=ts[2],day=ts[3],month=ts[4],day_of_week=ts[5]),args=args,kwargs=kwargs)
            self.jobs.items().append({job.id:job})
            self.jobs_ids.append({'md5':_id,'id':job.id})
            self.app.logger.info('add job sucessfull ' + "\tjob_id:"+ job.id+ "\tcron:"+ cron + "\tcommond"+ str(command) +"\tcallback"+ str(callback) )
            return job.id
        except Exception as err:
            self.app.logger.error(err)


    def _get_func(self,func=''):
        if isinstance(func,str):
            ctrl=re.split(r'\.',func)
            if len(ctrl)==2:
                return getattr(self.app.loader.ctrl(ctrl[0]),ctrl[1])
            else:
                return globals()[func]
        else:
            return func

    def remove_job(self,id):
        self.scheduler.remove_job(id)

    def pause(self,id):
        self.scheduler.pause_job(id)

    def resume(self,id):
        self.scheduler.resume_job(id)

    def get_schedule(self):
        return self.scheduler

    def stop(self):
        for ids in self.jobs_ids:
            self.pause(ids['id'])








def aa(r):
    print('xxx')
    print(r)



if __name__=='__main__':
    cron=CI_Cron()
    # a=eval('cron.test')
    # print(a)
    import time
    import sys
    # sys.exit()
    id=cron.add_cron('*/1 * * * * *','cron.test',aa='asdfasdf',ccc='asdf')
    eval('cron.test')
    cron.start()
    time.sleep(2)
    cron.stop()


    # cron.remove_job(id)
    while True:
        pass




