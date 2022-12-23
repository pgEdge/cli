
source buildSrc.sh

BANNER="PCRE – Supports regular expressions. Required by the NGINX Core and Rewrite modules."
v=8.45
d=pcre-$v
f=$d.tar.gz
u=https://sourceforge.net/projects/pcre/files/pcre/$v
buildSrc $v $d $f $u  ./configure 

BANNER="ZLIB – Supports header compression. Required by the NGINX Gzip module."
v=1.2.12
d=zlib-$v
f=$d.tar.gz
u=http://zlib.net
buildSrc $v $d $f $u  ./configure

BANNER="OPENSSL – Supports the HTTPS protocol. Required by the NGINX SSL module and others."
v=1.1.1q
d=openssl-$v
f=$d.tar.gz
u=http://www.openssl.org/source
buildSrc $v $d $f $u  ./config 

exit

