    
FROM alpine


#ADD pip.conf /etc/pip.conf
RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.4/main/" > /etc/apk/repositories && \
apk update && \
apk add git gcc libffi-dev musl-dev openssl-dev cmake  && \
apk add python py-paramiko py-gunicorn py-pip python-dev py-requests py-redis py-mysqldb py-lxml py-yaml py-curl && \
pip install falcon requests gevent pymysql pexpect redis kazoo memcache_wrapper DBUtils jinja2  && \

#### common packages ####
#apk add  python py-setuptools 	py-libvirt py-pip python-dev gcc  libusb py-pip python-dev gcc linux-headers gcc git libffi-dev musl-dev openssl-dev perl py-pip python python-dev sshpass  && \
#pip install libvirt-python
#pip install requests dnspython IPy XlsxWriter  scapy pexpect paramiko fabric ansible gevent netmiko docker-py kazoo falcon peewee gunicorn pyzabbix redis kazoo pika kafka-python autojenkins ldap3 boto psutil ansible elasticsearch  simplejson requests python-dateutil lxml

#### end common packages ####

apk del gcc libffi-dev musl-dev openssl-dev 


RUN mkdir -p /data/pyapp && cd /data/pyapp &&  git clone https://github.com/sjqzhang/PyCodeigniter.git && cd PyCodeigniter && python setup.py install && cp app.py .. && cd .. && rm -rf PyCodeigniter 

WORKDIR /data/pyapp

#ENTRYPOINT ["python","app.py"]
CMD ["python","app.py"]
