#!/bin/bash
cd "$(dirname "$0")"

source common.env

if [ "$BLD" == "" ]; then
  echo ERROR: Invalid Environment
  exit 1
fi

sudo mkdir -p /opt/pgbin-build
rc=$?
if [ "$rc" != "0" ]; then
  exit 1
fi

sudo mkdir -p /opt/pgbin-build/pgbin/bin
sudo chown -R $owner_group /opt/pgbin-build
sudo mkdir -p /opt/pgcomponent
sudo chown $owner_group /opt/pgcomponent

cd $BLD
rc=$?
if [ "$rc" != "0" ]; then
  exit 1
fi

cp -pv $CT/devel/pgbin/build/*.sh .

