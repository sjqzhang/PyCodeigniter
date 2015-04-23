#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



import os
import sys
import logging
import inspect
import re
import imp


class CI_Loader(object):
    def __init__(self,**kwargs):
        self.application_path= kwargs['application_path']
        self.app=kwargs['app']
        self.app.loader=self
        self.kwargs=kwargs
        self.app_modules_list=['helpers','library','models','controllers']
        self.modules={}
        self.classes={}
        self.sys_path=sys.path
        for m in self.app_modules_list:
            self.modules[m]={}
        map(self._load_application,self.app_modules_list)

    def cls(self,name):
        return self.classes[name]
    def model(self,name):
        return self._load('models',name)
    def ctrl(self,name):
        return self._load('controllers',name)
    def helper(self,name):
        return self._load('helpers',name)
    def library(self,name):
        return self._load('library',name)
    def _load(self,categroy,name):
        try:
            return self.modules[categroy][name]['instance']
        except KeyError as e:
            self.app.logger.error(name+" not found")
    def load_file(self,filename):
        try:
            name=filename.replace('.py','')
            name=os.path.basename(name)
            fn_, path, desc = imp.find_module(name, [os.path.dirname(filename)])
            mod = imp.load_module(name, fn_, path, desc)
            return mod
        except Exception as e:
            self.app.logger.error("load module error filename:"+ filename +str(e))

    def load_module(self,mod_dir):
        try:
            names = {}
            modules = []
            funcs = {}
            for fn_ in os.listdir(mod_dir):
                if fn_.startswith('_'):
                    continue
                if (fn_.endswith(('.py', '.pyc', '.pyo', '.so')) or os.path.isdir(fn_)):
                    extpos = fn_.rfind('.')
                    if extpos > 0:
                        _name = fn_[:extpos]
                    else:
                        _name = fn_
                    names[_name] = os.path.join(mod_dir, fn_)
            for name in names:
                try:
                    fn_, path, desc = imp.find_module(name, [mod_dir])
                    mod = imp.load_module(name, fn_, path, desc)
                except:
                    continue
                modules.append(mod)
            for mod in modules:
                for attr in dir(mod):
                    if attr.startswith('_'):
                        continue
                    #
                    if callable(getattr(mod, attr)):
                        func = getattr(mod, attr)
                        if isinstance(func, type):
                            if any(['Error' in func.__name__, 'Exception' in func.__name__]):
                                continue
                        try:
                            funcs['{0}.{1}'.format(mod.__name__, attr)] = func
                        except Exception as e:
                            self.app.logger.error("load module error dir:"+ mod_dir +str(e))
                            continue
            return funcs
        except Exception as e:
            self.app.logger.error("load module error dir:"+ mod_dir +str(e))





    def regcls(self,name,aclass):
        self.classes[name]=aclass


    def _load_application(self,module_name,path=None):
        if path==None:
            path=self.application_path
        module_path=path+os.path.sep+module_name
        if not os.path.isdir(module_path):
            self.app.logger.log(module_path+' not exists')
            return
        if module_path not in sys.path:
            sys.path=self.sys_path
            sys.path.insert(0,module_path)
        files=os.listdir(path+os.path.sep+module_name)

        for file in files:
            file_path=path+os.path.sep+module_name+os.path.sep+ file
            if os.path.isfile(file_path) and file.endswith('.py') and file!='__init__.py':
                try:
                    module=file.split('.')[0]
                    # __import__(module)
                    exec("from "+module+" import "+module )
                    cmodule=__import__(module)

                    aclass= getattr(cmodule,module)

                    has_init=hasattr(aclass,'__init__')
                    if has_init:
                        init_member=getattr(aclass,'__init__')
                        arginfo= str(init_member)
                        if re.match(r'^<unbound method',arginfo):
                            arginfo= inspect.getargspec(init_member)
                        else:
                            arginfo=''
                    else:
                        arginfo=''
                    if module not in self.modules[module_name].keys():
                        _instance=None
                        try:

                            if str(arginfo).find('kwargs')>0:
                                _instance= eval(module+'(**self.kwargs)')
                            else:
                                _instance= eval(module+'()')

                            if not hasattr(_instance,'app'):
                                setattr(_instance,'app',self.app)
                            if not hasattr(_instance,'db'):
                                setattr(_instance,'db',self.app.db)
                            if not hasattr(_instance,'logger'):
                                setattr(_instance,'logger',self.app.logger)
                            if _instance!=None and module_name=='controllers' and not hasattr(_instance,'model') and self.modules['models'].has_key(module+'Model'):
                                setattr(_instance,'model',self.model(module+'Model'))
                                # print(self.model(module+'Model'))
                                # print(self.model(module+'Model').search())

                        except Exception as e:
                            self.app.logger.error('create '+ module+ ' failed ,please check parameters, '+str(e))
                            # print(file_path, e)

                        self.modules[module_name][module]={'aclass':getattr( cmodule ,module),'instance':_instance}
                        self.classes[module]=getattr(cmodule ,module)

                except Exception as e:
                    self.app.logger.error("load "+module+" module error "+str(e))

            elif os.path.isdir(file_path):
                self._load(module_name,file_path)










if __name__=='__main__':

    #loader=CI_Loader(r'E:\python\study\Codeigniter\system',r'E:\python\study\Codeigniter\application')
    loader=CI_Loader(application_path=r'E:\python\study\Codeigniter\application',app=None)

    print(loader.model('SearchModel'))


