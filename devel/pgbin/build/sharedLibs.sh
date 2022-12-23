
apt --version 1> /dev/null 2> /dev/null
rc=$?

if [ `uname` == "Linux" ]; then
  if [ "$rc" == "0" ]; then
    lib64=/usr/lib/`arch`-linux-gnu
  else
    lib64=/usr/lib64/
  fi
elif [ `uname` == "Darwin" ]; then
  lib64=/usr/lib64
else
  echo "ERROR: Invalid Operating System."
  exit 1
fi 

isEL8=no
grep el8 /etc/os-release > /dev/null > 2&>1
rc=$?
if [ "$rc" == "0" ]; then
  isEL8=yes
fi
#echo isEL8=$isEL8

shared_lib=/opt/pgbin-build/pgbin/shared/lib/
mkdir -p $shared_lib
rm -f $shared_lib/*

cp -Pv $lib64/libcrypt*.so*   $shared_lib/.
cp -Pv $lib64/libbz2.so.*     $shared_lib/.
cp -Pv $lib64/libz.so.*       $shared_lib/.
cp -Pv $lib64/libssl*         $shared_lib/.
cp -Pv $lib64/libkrb5*        $shared_lib/.
cp -Pv $lib64/libgssapi*      $shared_lib/.
cp -Pv $lib64/libldap*        $shared_lib/.
cp -Pv $lib64/libedit*        $shared_lib/.
cp -Pv $lib64/libxml2.so.*    $shared_lib/.
cp -Pv $lib64/libxslt.so*     $shared_lib/.
cp -Pv $lib64/liblber*        $shared_lib/.
cp -Pv $lib64/libsasl2*       $shared_lib/.
cp -Pv $lib64/libevent*       $shared_lib/.
cp -Pv $lib64/libreadline*    $shared_lib/.
cp -Pv $lib64/libk5crypto.so.*     $shared_lib/.
cp -Pv $lib64/libpam.so.*          $shared_lib/.
cp -Pv $lib64/libpython3*          $shared_lib/.
cp -Pv $lib64/libtinfo.so.*        $shared_lib/.
cp -Pv $lib64/libnss3*             $shared_lib/.
cp -Pv $lib64/libnspr4*            $shared_lib/.
cp -Pv $lib64/libnssutil3*         $shared_lib/.
cp -Pv $lib64/libsmime*            $shared_lib/.
cp -Pv $lib64/libplds4*            $shared_lib/.
cp -Pv $lib64/libplc4*             $shared_lib/.
cp -Pv $lib64/libpcre.so.*         $shared_lib/.
cp -Pv $lib64/libfreebl3.so        $shared_lib/.
cp -Pv $lib64/libcap*              $shared_lib/.
cp -Pv $lib64/libaudit*            $shared_lib/.
cp -Pv $lib64/libresolv-2*         $shared_lib/.
cp -Pv $lib64/libresolv.so.2       $shared_lib/.
cp -Pv $lib64/liblzma.so.*         $shared_lib/.
cp -Pv $lib64/libcom_err.so.*      $shared_lib/.
cp -Pv $lib64/libkeyutils.so.*     $shared_lib/.
cp -Pv $lib64/libjson-c*           $shared_lib/.

##cp -Pv $lib64/llvm5.0/lib/*.so*    $shared_lib/.
cp -Pv $lib64/libffi*.so*          $shared_lib/.

# plv8
##cp -Pv $lib64/libc++.so.*          $shared_lib/.

# bouncer (small enough lib to include by default)
cp -Pv /lib64/libcares*            $shared_lib/.

# oracle_fdw
#oraclient=/opt/oracleinstantclient/instantclient_19_8
#cp -Pv $oraclient/libclntsh.so.19.1 $shared_lib/.
#cp -Pv $oraclient/libclntshcore.so.19.1 $shared_lib/.
#cp -Pv $oraclient/libmql1.so        $shared_lib/.
#cp -Pv $oraclient/libipc1.so        $shared_lib/.
#cp -Pv $oraclient/libnnz19.so       $shared_lib/.
#cp -Pv $lib64/libselinux*           $shared_lib/.
#cp -Pv $lib64/libaio*               $shared_lib/.
#cp -Pv $lib64/libtirpc*             $shared_lib/.


# tds_fdw
#cp -Pv $lib64/libsybdb.so.*           $shared_lib/.
#cp -Pv $lib64/libhogweed.so.*         $shared_lib/.
#cp -Pv $lib64/libgnutls.so.*          $shared_lib/.
#cp -Pv $lib64/libnettle.so.*          $shared_lib/.
#cp -Pv $lib64/libgmp.so.*             $shared_lib/.
#cp -Pv $lib64/libp11-kit.so.*         $shared_lib/.
#cp -Pv $lib64/libtasn1.so.*           $shared_lib/.
#cp -Pv $lib64/libffi.so.*             $shared_lib/.

# fixup for oraclefdw
#cd $sl
#ln -s libnsl.so.2 libnsl.so.1

## cleanups at the end #################
cd $shared_lib
ln -fs libcrypt.so.1 libcrypt.so

sl="$shared_lib/."
rm -f $sl/*.a
rm -f $sl/*.la
rm -f $sl/*libboost*test*


