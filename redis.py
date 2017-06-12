#!/usr/bin/python
from __future__ import print_function
import os
import urllib2
import re
import tarfile
import shutil
import subprocess
import sys
import socket

def install_sys_redis():
    try:
        if sys.argv[1] == 'phponly':
            return
    except:
        pass
    os.system("yum install -y epel-release")
    os.system("yum update")
    os.system("yum install -y redis jemalloc")
    with open('/etc/yum.repos.d/epel.repo', r) as fh:
        epel_repo = fh.readlines()
    os.system("systemctl start redis")
    os.system("systemctl enable redis")

def php_redis_url():
    r = urllib2.urlopen('https://pecl.php.net/package/redis', timeout = 240)
    for line in r.readlines():
        if '/package/redis/' not in line:
            continue
        if re.search('\dRC', line):
            continue
        if '/get/redis' in line:
            url = re.search('(/get/redis-\d{1,3}\.\d{1,3}\.\d{1,3}\.tgz)', line)
            try:
                return 'https://pecl.php.net/{0}'.format(url.group(1))
            except:
                print('failed to get url')
            break

def get_php_versions():
    php_list = []
    for fn in os.listdir('/opt/cpanel/'):
        if not fn.startswith('ea-php'):
            continue
        if os.path.isfile('/opt/cpanel/{0}/root/usr/bin/php'.format(fn)):
            php_list.append(fn)
    return php_list

def build_php_redis(php_version, redis_dir_name):
    os.chdir('/usr/local/src')
    for dir in os.listdir('.'):
        if 'redis-' in dir:
            redis_dir_name = dir
    os.chdir(redis_dir_name)
    os.system('/opt/cpanel/{0}/root/usr/bin/phpize'.format(php_version))
    os.system('./configure --with-php-config=/opt/cpanel/{0}/root/usr/bin/php-config'.format(php_version))
    os.system('make')
    extension_dir = get_extension_dir('/opt/cpanel/{0}/root/usr/bin/php'.format(php_version))
    shutil.copy2('/usr/local/src/{0}/modules/redis.so'.format(redis_dir_name), '/opt/cpanel/{0}/root/usr/lib64/php/modules/'.format(php_version))
    with open('/opt/cpanel/{0}/root/etc/php.d/redis.ini'.format(php_version), 'w') as fh:
        print('extension = redis.so', file=fh)
    os.chdir('/usr/local/src')
    shutil.rmtree('/usr/local/src/{0}'.format(redis_dir_name))
    return

def get_extension_dir(php_binary):
    #print('trying {}'.format(php_binary))
    p = subprocess.Popen(php_binary, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write("<? echo ini_get('extension_dir'); ?>\n")
    p = p.communicate()
    path = re.search('/opt/.*', p[0])
    try:
        return path.group(0)
    except:
        print('failed to detect extensions_dir')
        exit(0)

def download_php_redis():
    os.chdir('/usr/local/src')
    url = php_redis_url()
    print('trying url {0}'.format(url))
    r = urllib2.urlopen(url, timeout=240)
    tar_name='redis.tar.gz'
    with open('redis.tar.gz', 'w') as fh:
        print(r.read(), file=fh)
    return tar_name


def untar_php_redis(tar_name):
    os.chdir('/usr/local/src')
    tar = tarfile.open(tar_name, "r:gz")
    tar.extractall()
    tar.close()
    for dir in os.listdir('.'):
        if 'redis-' in dir:
            redis_dir_name = dir
    os.chdir(redis_dir_name)
    return redis_dir_name

def main():
    socket.setdefaulttimeout(120.0)
    install_sys_redis()
    tar_name = download_php_redis()
    php_versions = get_php_versions()
    for php_version in php_versions:
        redis_dir_name = untar_php_redis(tar_name)
        build_php_redis(php_version, redis_dir_name)

if __name__ == '__main__':
    main()
