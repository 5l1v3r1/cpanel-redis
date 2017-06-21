## cPanel redis installer

+ Installs the redis server using the EPEL repo and yum
+ Sets redis to run on startup
+ Compiles the redis.so extension files for all versions of PHP installed

#### Requirements:
+ EasyApache4 or EA3
+ Python2.6 or 2.7

#### Usage:
> Run as root or sudoer with sudo

```
wget https://github.com/Leo675/cpanel-redis/blob/master/redis.py
python redis.py
```
