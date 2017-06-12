## cPanel redis installer

+ Installs the redis server using the EPEL repo and yum
+ Sets redis to run on startup
+ Compiles the redis.so extension files for all versions of PHP installed

#### Requirements:
+ EasyApache4
+ Python2.6 or 2.7

> Support for EasyApache3 will be added later

#### Usage:
> Run as root or sudoer with sudo

```wget https://github.com/Leo675/cpanel-redis/blob/master/redis.py
python redis.py```
