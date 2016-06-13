#!/usr/bin/env bash

is_install(){

 yy=$(echo echo `which "$1"`|grep -o "$1")


 if [ -z $yy ];then

  return 0

 else

  return 1

 fi

}

if [ -f /etc/system-release ];then
  sys=`grep -Eio "(centos|ubuntu)" /etc/system-release`
else
 sys=`grep -Eio "(centos|ubuntu)" /etc/issue`
fi


sys=$(echo $sys|tr '[A-Z]' '[a-z]')


URL=http://git.oschina.net/sjqzhang/pylib/raw/master
#URL=https://github.com/sjqzhang/pylib/raw/master/



install_centos(){

yum install -y "Development tools"
yum install -y python-devel
yum install -y wget
yum install -y unzip
yum install -y python-gevent


}

install_ubuntu(){

apt-get install -y build-essential
apt-get install -y python-dev
apt-get install -y wget
apt-get install -y unzip
apt-get install -y python-gevent


}





install_pip()
{
is_install pip

if [ $? -eq 0 ];then

wget --no-check-certificate  $URL/setuptools-0.6c11.tar.gz -O /tmp/setuptools-0.6c11.tar.gz

tar xzvf /tmp/setuptools-0.6c11.tar.gz

wget --no-check-certificate  $URL/pip-6.1.1.tar.gz  -O /tmp/pip-6.1.1.tar.gz

tar xzvf /tmp/pip-6.1.1.tar.gz

cd setuptools-0.6c11

python setup.py install

cd ..

cd pip-6.1.1

python setup.py install


fi

}

install_${sys}

install_pip





wget https://github.com/sjqzhang/PyCodeigniter/archive/master.zip -O PyCodeigniter.zip

unzip -o PyCodeigniter.zip


cd PyCodeigniter-master


pip install -r requirements.txt

python setup.py install
