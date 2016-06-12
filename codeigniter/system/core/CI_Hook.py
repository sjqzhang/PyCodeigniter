#!/usr/bin/env python
# -*- coding:utf8 -*-


from CI_Application import CI as app
import os,imp

class CI_Hook(object):

    def __init__(self):
        self.load_hook()

    def create_hook_handler(self,cfg):
        try:
            base_path= app.application_path
            paths = cfg.split(".")
            file_name = "%s.py" % paths[0]
            abs_path = "%s/hooks/%s" % (base_path,file_name)
            if not os.path.exists(abs_path):
                return
            ref =  imp.load_module(paths[0],*(imp.find_module(paths[0],["%s/hooks" % base_path])) )
            paths = paths[1:]
            if len(paths) == 1:
                if hasattr(ref,paths[0]):
                    return getattr(ref,paths[0])
            if len(paths) == 2:
                cls =  getattr(ref,paths[0])
                ref = cls()
                if hasattr(ref,paths[1]):
                    return getattr(ref,paths[1])
        except BaseException as e:
            pass



    def load_hook(self):
        if app.config==None or 'hooks' not in app.config.keys():
            return
        hooks = app.config['hooks']
        hook_keys=['pre_system','pre_controller','post_controller_constructor','post_controller','display_override']

        for key in hooks.keys():
            if not key in hook_keys:
                continue
            hook_val = hooks[key]
            if type(hook_val) == list:
                setattr(self,key,[])
                for cfg in hook_val:
                    handler = self.create_hook_handler(cfg)
                    if hasattr(handler,'__call__'):
                        getattr(self,key).append(handler)

            if type(hook_val) == str :
                handler = self.create_hook_handler(hook_val)
                if hasattr(handler,'__call__'):
                    setattr(self,key,handler)


    def _call_hook(self,hook_name,*args,**argv):
        if not hasattr(self,hook_name):
            return
        hook = getattr(self,hook_name)
        if None == hook:
            return
        if type(hook) == list:
            for hcall in hook:
                if False ==  hcall(*args,**argv):
                    return False
            return
        return hook(*args,**argv)


    def call_pre_system(self,*args,**argv):
        return self._call_hook('pre_system',*args,**argv)

    def call_pre_controller(self,*args,**argv):
        return self._call_hook('pre_controller',*args,**argv)

    def call_post_controller_constructor(self,*args,**argv):
        return self._call_hook('post_controller_constructor',*args,**argv)

    def call_post_controller(self,*args,**argv):
        return self._call_hook('post_controller',*args,**argv)

    def call_display_override(self,*args,**argv):
        return self._call_hook('display_override',*args,**argv)
