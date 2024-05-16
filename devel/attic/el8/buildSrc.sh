set -e -x

buildSrc () {
  ver="$1"
  dir="$2"
  file="$3"
  url="$4"
  config="$5"
  basedir=/opt/tools

  echo " "
  echo "#####################################################################################"
  echo "# $BANNER"
  echo "#####################################################################################"
  echo "#     ver=$ver"
  echo "#     dir=$dir"
  echo "#    file=$file"
  echo "#     url=$url"
  echo "#  config=$config"
  echo "# basedir=$basedir"
  echo "#####################################################################################"

  numparms=5
  if [ "$#" -ne $numparms ]; then
    echo "ERROR: must be $numparms parms"
    exit 1
  fi

  echo "# cleaning up cruft ..."
  rm -rf $basedir/$dir*
  mkdir -p $basedir
  cd $basedir

  echo "# downloading $file from $url ..."
  wget $url/$file

  echo "# expanding $file ..."
  tar -xf $file

  cd $dir
  log="make-$dir.log"
  echo "# config with $config to $log ..."
  "$config" > $log 

  echo "# compile to $log ..."
  make -j4 >> $log 

  echo "# install"
  sudo make install > makeinstall-$dir.log
}

