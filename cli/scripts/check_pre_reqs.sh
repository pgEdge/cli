#!/bin/bash

#  Copyright 2022-2025 PGEDGE  All rights reserved. #

cd "$(dirname "$0")"

parms=`echo $@`


echoX () {
  if [ "$isJson" == "True" ]; then
    echo "{\"msg\": \"$1\"}"
  else
    echo "$1"
  fi
}


isEL () {

  if [ -f "/etc/redhat-release" ]; then
      return
  fi

}



isAMD64 () {
  if [ `uname -m` == 'x86_64' ]; then
    echoX '#     AMD64 - OK'
    return
  fi

  echoX 'ERROR: only supported on AMD64' 
  exit 1
}


isUBU () {
  ver="$1.04"
  cat /etc/os-release | grep VERSION_ID | grep $ver > /dev/null
  rc=$?
  if [ $rc == "0" ]; then
    echoX "#       UBU$1 - OK"
    return
  fi

  echoX "ERROR: only supported on Ubuntu $ver"
  exit 1
}


########################################
#              MAINLINE                #
########################################

echoX "# pre-req's: $parms"

for req in "$@"
do
  if [ "${req:0:2}" == "EL" ]; then
    ver=${req:2:1}
    isEL $ver 
  elif [ "${req:0:3}" == "UBU" ]; then
    ver=${req:3:2}
    isUBU $ver
  elif [ "$req" == "AMD64" ]; then
    isAMD64
  else
    echoX "ERROR: invalid pre-req ($req)"
    exit 1
  fi
done

exit 0

