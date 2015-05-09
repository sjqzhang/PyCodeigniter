#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



import os
import sys
import time
import inspect
import re
import imp



try:
    import thread
except ImportError as e:
    import _thread as thread


class CI_Loader(object):
    def __init__(self,**kwargs):
        self.application_path= kwargs['application_path']
        self.app=kwargs['app']
        self.app.loader=self
        self.kwargs=kwargs
        self.app_modules_list=['helpers','library','models','controllers']
        self.modules={}
        self.classes={}
        self.files={}
        self.sys_path=sys.path
        for m in self.app_modules_list:
            self.modules[m]={}
        map(self._load_application,self.app_modules_list)

        try:
            if self.app.config['server']['envroment']=='development' or self.app.config['server']['envroment']=='dev':
                thread.start_new_thread(self.check,(),)
        except Exception as e:
            self.app.logger.error(e)


    def check(self):
        while True:
            try:
                for path in self.files.keys():
                    # print(path)
                    if os.stat(path).st_mtime> self.files[path]:
                        filename=os.path.basename(path)
                        category=os.path.basename(os.path.dirname(path))
                        module=self.load_file(path)
                        if module.__name__ in dir(module):
                            m=module.__name__
                            del self.modules[category][m]
                            self._register_instance(module,m,category)
                            self.files[path]=os.stat(path).st_mtime
                            continue

                        for m in dir(module):
                            if (isinstance(getattr(module,m),type) or type(getattr(module,m)).__name__=='classobj')  and module!=None:
                                del self.modules[category][m]
                                self._register_instance(module,m,category)
                                self.files[path]=os.stat(path).st_mtime

                        # name=filename.split('.')[0]
                        # if category in self.modules.keys() and name in self.modules[category]:
                        #     del self.modules[category][name]
                        # self._load(category,name,True)
                        # self.files[path]=os.stat(path).st_mtime
                time.sleep(2)
            except Exception as e:
                self.app.logger.error(e)





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
    def get_module_name(self,name,categroy):
        for key in self.modules[categroy].keys():
            if name.lower()==key.lower():
                return key

    def _load(self,categroy,name,is_reload=False,count=0):
        try:
            if count>1:
                self.app.logger.error( "load "+ categroy+"  "+ name+" fail")
                return None
            if not is_reload:
                shortname=os.path.basename(name)
                mname=self.get_module_name(shortname,categroy)
                return self.modules[categroy][mname]['instance']
            else:
                raise KeyError('reload')
        except KeyError as e:
            dirctory=os.path.dirname(name)
            module_name=os.path.basename(name)
            if dirctory!='':
                path=self.application_path+os.path.sep+categroy+os.path.sep+dirctory
            else:
                path=self.application_path+os.path.sep+categroy
            file_name='';
            for file in os.listdir(path):
                if file.split('.')[0].lower()==module_name.lower():
                    file_name=path+os.path.sep+file
                    break
            if file_name!='':
                module=self.load_file(file_name)
                if module.__name__ in dir(module):
                    m=module.__name__
                    if (isinstance(getattr(module,m),type) or type(getattr(module,m)).__name__=='classobj')  and module!=None and not m.startswith('_'):
                        self._register_instance(module,m,categroy)
                        return self._load(categroy,name,count=count+1)

                for m in dir(module):
                    if (isinstance(getattr(module,m),type) or type(getattr(module,m)).__name__=='classobj')  and module!=None:
                        self._register_instance(module,m,categroy)
                return self._load(categroy,name,count=count+1)
            else:
                self.app.logger.error(name+" not found")
                return None
    def load_file(self,filename):
        try:
            # print(filename)
            if filename.endswith('.py') and filename not in self.files.keys():

                self.files[filename]=os.stat(filename).st_mtime
                # print(filename)
                # print(os.stat(filename).st_ctime)

            name=filename.replace('.pyc','').replace('.py','')

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
        is_autoload=True
        autoload={}
        for file in files:
            file_path=path+os.path.sep+module_name+os.path.sep+ file
            if file=='__init__.py':
                module=self.load_file(file_path)
                if hasattr(module,'autoload'):
                    autoload=getattr(module,'autoload')
                    if not isinstance(autoload,dict):
                        autoload={}
                    elif isinstance(autoload,dict):
                        is_autoload=False
                        break
                    else:
                        self._load_application3(module_name,path)
                        return;

        if is_autoload:
            self._load_application3(module_name,path)
            return;

        if len(autoload)==0:
            return;

        for file in files:
            file_path=path+os.path.sep+module_name+os.path.sep+ file
            if os.path.isfile(file_path) and (file.endswith('.py') or file.endswith('.pyc')) and file!='__init__.py':
                for m in autoload.keys():
                    if m==file.split('.')[0]:
                        module=self.load_file(file_path)
                        self._register_instance(module,autoload[m],module_name)
                        break;

    def _load_application3(self,module_name,path=None):
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
            if os.path.isfile(file_path) and (file.endswith('.py') or file.endswith('.pyc')) and file!='__init__.py':
                module=self.load_file(file_path)
                # print((module.__name__))
                if module.__name__ in dir(module):
                    m=module.__name__
                    if (isinstance(getattr(module,m),type) or type(getattr(module,m)).__name__=='classobj')  and module!=None and not m.startswith('_'):
                        self._register_instance(module,m,module_name)
                        continue

                for m in dir(module):
                    if (isinstance(getattr(module,m),type) or type(getattr(module,m)).__name__=='classobj')  and module!=None and not m.startswith('_'):
                        self._register_instance(module,m,module_name)



    def _register_instance(self, module, module_name, module_category_name):

        aclass = getattr(module, module_name)
        # print(aclass)
        # aclass.init__instance=init_instace
        # print(dir(aclass))
        has_init = hasattr(aclass, '__init__')
        if has_init:
            init_member = getattr(aclass, '__init__')
            arginfo = str(init_member)
            if re.match(r'^<unbound method', arginfo):
                arginfo = inspect.getargspec(init_member)
            else:
                arginfo = ''
        else:
            arginfo = ''
        if module_name not in self.modules[module_category_name].keys():
            _instance = None
            try:

                if str(arginfo).find('kwargs') > 0:

                    # _instance = eval(module_name + '(**self.kwargs)')
                    init=getattr(module,module_name)
                    _instance=init(**self.kwargs)

                else:
                    # _instance = eval(module_name + '()')
                    init=getattr(module,module_name)
                    _instance=init()

                # instace_metho= getattr(_instance,'init__instance',None)
                # print(instace_metho)
                # if instace_metho!=None:
                # instace_metho(self.app)

                if not hasattr(_instance, 'app'):
                    setattr(_instance, 'app', self.app)
                if not hasattr(_instance, 'db'):
                    setattr(_instance, 'db', self.app.db)
                if not hasattr(_instance, 'logger'):
                    setattr(_instance, 'logger', self.app.logger)
                if _instance != None and module_category_name == 'controllers' and not hasattr(_instance, 'model') and \
                        (module_name + 'Model' in self.modules['models'].keys() or module_name + '_model' in self.modules['models'].keys()):
                    setattr(_instance, 'model', self.model(module_name + 'Model'))
                    # print(self.model(module+'Model'))
                    # print(self.model(module+'Model').search())
                self.app.logger.info('load module '+ module_name+ ' of '+ module_category_name+ ' successfull')

            except Exception as e:
                self.app.logger.error('create ' + module_name + ' of  '+ module_category_name + ' failed ,please check parameters, ' + str(e))
                # print(file_path, e)

            self.modules[module_category_name][module_name] = {'aclass': getattr(module, module_name), 'instance': _instance}
            self.classes[module_name] = getattr(module, module_name)

    def _load_application2(self,module_name,path=None):
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
                    # globals()['ci']=self.app
                    exec("from "+module+" import "+module )
                    # exec("from "+module+" import *")
                    cmodule=__import__(module)

                    self._register_instance(cmodule, module, module_name)

                except Exception as e:
                    self.app.logger.error("load "+module+" module error "+str(e))

            elif os.path.isdir(file_path):
                self._load(module_name,file_path)










if __name__=='__main__':

    #loader=CI_Loader(r'E:\python\study\Codeigniter\system',r'E:\python\study\Codeigniter\application')
    loader=CI_Loader(application_path=r'E:\python\study\Codeigniter\application',app=None)

    print(loader.model('SearchModel'))


