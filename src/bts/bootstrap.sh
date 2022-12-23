#!/bin/bash
cd "$(dirname "$0")"

etcdV=3.4.14
rkeV=1.2.3

source getPKMG.sh
if [ "$PKMG" == "yum" ]; then
  sudo yum -y install epel-release
  if [ "$VER_OS" == "8" ]; then
    sudo yum config-manager --set-enabled PowerTools
  fi
  sudo yum -y install wget git
  sudo yum -y groupinstall 'development tools'
else
  sudo apt install -y wget git
  sudo apt install -y build-essential libssl-dev libffi-dev
fi

./install-python3

./install-jdk11

./install-nginx

./install-etcd $etcdV

./install-docker

./install-kubectl

#./install-rke $rkeV

#./install-rancher

echo ""
echo "Goodbye!"
exit 0

