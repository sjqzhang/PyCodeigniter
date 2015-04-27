from distutils.core import setup

setup(
    name='PyCodeigniter',
    version='0.1.9',
    packages=['', 'codeigniter', 'codeigniter.system', 'codeigniter.system.core', 'codeigniter.application',
              'codeigniter.application.config', 'codeigniter.application.models',
              'codeigniter.application.controllers','codeigniter.application.helpers','codeigniter.application.library'],
    url='https://github.com/sjqzhang/PyCodeigniter',
    license='GPL',
    requires=['pymysql','DBUtils','gevent'],
    author='s_jqzhang',
    author_email='s_jqzhang@163.com',
    description="Codeigniter(PHP) implement by python\n If you want to build high performance service you'd better use gevent. "
)
