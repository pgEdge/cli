

function osxCopySharedLibs {
  lib=/usr/lib
  cp $lib/libxml2.2.dylib          $shared_lib/.

  loc=/usr/local/opt
  cp $loc/lz4/lib/liblz4.1.dylib   $shared_lib/.
  cp $loc/zstd/lib/libzstd.1.dylib $shared_lib/.
}



function linuxCopySharedLibs {
  lib=/usr/lib

  cp -Pv $lib/libcrypt*.so*   $shared_lib/.
  cp -Pv $lib/libbz2.so.*     $shared_lib/.
  cp -Pv $lib/libz.so.*       $shared_lib/.
  cp -Pv $lib/libssl*         $shared_lib/.
  cp -Pv $lib/libkrb5*        $shared_lib/.
  cp -Pv $lib/libgssapi*      $shared_lib/.
  cp -Pv $lib/libldap*        $shared_lib/.
  cp -Pv $lib/libedit*        $shared_lib/.
  cp -Pv $lib/libxml2.so.*    $shared_lib/.
  cp -Pv $lib/libxslt.so*     $shared_lib/.
  cp -Pv $lib/liblber*        $shared_lib/.
  cp -Pv $lib/libsasl2*       $shared_lib/.
  cp -Pv $lib/libevent*       $shared_lib/.
  cp -Pv $lib/libreadline*    $shared_lib/.
  cp -Pv $lib/libk5crypto.so.*     $shared_lib/.
  cp -Pv $lib/libpam.so.*          $shared_lib/.
  cp -Pv $lib64/libpython3.so      $shared_lib/.
  cp -Pv $lib64/libpython3.9*      $shared_lib/.
  cp -Pv $lib/libtinfo.so.*        $shared_lib/.
  cp -Pv $lib/libnss3*             $shared_lib/.
  cp -Pv $lib/libnspr4*            $shared_lib/.
  cp -Pv $lib/libnssutil3*         $shared_lib/.
  cp -Pv $lib/libsmime*            $shared_lib/.
  cp -Pv $lib/libplds4*            $shared_lib/.
  cp -Pv $lib/libplc4*             $shared_lib/.
  cp -Pv $lib/libpcre.so.*         $shared_lib/.
  cp -Pv $lib/libfreebl3.so        $shared_lib/.
  cp -Pv $lib/libcap*              $shared_lib/.
  cp -Pv $lib/libaudit*            $shared_lib/.
  cp -Pv $lib/libresolv-2*         $shared_lib/.
  cp -Pv $lib/libresolv.so.2       $shared_lib/.
  cp -Pv $lib/liblzma.so.*         $shared_lib/.
  cp -Pv $lib/libcom_err.so.*      $shared_lib/.
  cp -Pv $lib/libkeyutils.so.*     $shared_lib/.
  cp -Pv $lib/libjson-c*           $shared_lib/.

  ##cp -Pv $lib/llvm5.0/lib/*.so*    $shared_lib/.
  cp -Pv $lib/libffi*.so*          $shared_lib/.

  # plv8
  ##cp -Pv $lib/libc++.so.*          $shared_lib/.

  # bouncer (small enough lib to include by default)
  cp -Pv /lib/libcares*            $shared_lib/.

  # oracle_fdw
  #oraclient=/opt/oracleinstantclient/instantclient_19_8
  #cp -Pv $oraclient/libclntsh.so.19.1 $shared_lib/.
  #cp -Pv $oraclient/libclntshcore.so.19.1 $shared_lib/.
  #cp -Pv $oraclient/libmql1.so        $shared_lib/.
  #cp -Pv $oraclient/libipc1.so        $shared_lib/.
  #cp -Pv $oraclient/libnnz19.so       $shared_lib/.
  #cp -Pv $lib/libselinux*           $shared_lib/.
  #cp -Pv $lib/libaio*               $shared_lib/.
  #cp -Pv $lib/libtirpc*             $shared_lib/.

  # tds_fdw
  #cp -Pv $lib/libsybdb.so.*           $shared_lib/.
  #cp -Pv $lib/libhogweed.so.*         $shared_lib/.
  #cp -Pv $lib/libgnutls.so.*          $shared_lib/.
  #cp -Pv $lib/libnettle.so.*          $shared_lib/.
  #cp -Pv $lib/libgmp.so.*             $shared_lib/.
  #cp -Pv $lib/libp11-kit.so.*         $shared_lib/.
  #cp -Pv $lib/libtasn1.so.*           $shared_lib/.
  #cp -Pv $lib/libffi.so.*             $shared_lib/.

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

}

########################################################
##                MAINLINE                            ##
########################################################

set -x

shared_lib=/opt/pgbin-build/pgbin/shared/lib/
mkdir -p $shared_lib
rm -f $shared_lib/*

if [ `uname` == "Linux" ]; then
  linuxCopySharedLibs
else
  osxCopySharedLibs
fi

