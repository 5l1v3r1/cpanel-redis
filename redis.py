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
    os.system("service start redis")
    os.system("chkconfig redis on")

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
    if php_list:
        return php_list
    for fn in os.listdir('/opt/'):
        if not fn.startswith('php'):
            continue
        if os.path.isfile('/opt/{0}/bin/php'.format(fn)):
            php_list.append(fn)
    if php_list:
        return php_list
    else:
        return ['system']

def build_php_redis(php_version, redis_dir_name):
    os.chdir('/usr/local/src')
    for dir in os.listdir('.'):
        if 'redis-' in dir:
            redis_dir_name = dir
    os.chdir(redis_dir_name)
    if php_version == 'system':
        phpize = '/usr/bin/phpize'
        php_binary = '/usr/bin/php'
        php_config = '/usr/bin/php-config'
        main_ini = '/usr/local/lib/php.ini'
        additional_dir = None
    elif php_version.startswith('php'):
        if php_version == 'php52':
            return
        phpize = '/opt/{0}/bin/phpize'.format(php_version)
        php_binary = '/opt/{0}/bin/php'.format(php_version)
        php_config = '/opt/{0}/bin/php-config'.format(php_version)
        main_ini = '/opt/{0}/lib/php/php.ini'.format(php_version)
        additional_dir = None
    else:
        phpize = '/opt/cpanel/{0}/root/usr/bin/phpize'.format(php_version)
        php_binary = '/opt/cpanel/{0}/root/usr/bin/php'.format(php_version)
        php_config = '/opt/cpanel/{0}/root/usr/bin/php-config'.format(php_version)
        additional_dir = '/opt/cpanel/{0}/root/etc/php.d/'.format(php_version)

    os.system(phpize)
    os.system('./configure --with-php-config={0}'.format(php_config))
    os.system('make')
    extension_dir = get_extension_dir(php_binary)
    shutil.copy2('/usr/local/src/{0}/modules/redis.so'.format(redis_dir_name), extension_dir)
    if additional_dir:
        with open('{0}/redis.ini'.format(additional_dir), 'w') as fh:
            print('extension = redis.so', file=fh)
    else:
        with open(main_ini, 'r+a') as fh:
            if 'extension = redis.so' not in fh.readlines():
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
