#!/bin/bash
cd "$(dirname "$0")"

ver=3.7.1
url=http://apache.osuosl.org/zookeeper

echo " "
echo "## INSTALL ZOOKEEPER v$ver ##################################"

sudo useradd zk -m
sudo usermod -a -G wheel zk
sudo usermod --shell /bin/bash zk

zookD=apache-zookeeper-$ver-bin
zookF=$zookD.tar.gz
rm -rf $zookF
wget $url/zookeeper-$ver/$zookF
tar xzf $zookF

zkDir=/opt/zookeeper
sudo rm -rf $zkDir
sudo mv $zookD $zkDir
sudo cp example.config $zkDir/conf/zoo.cfg
#sudo cp example-log4j.properties $zkDir/conf/log4j.properties
sudo chown zk:zk -R $zkDir

sudo cp example.service  /etc/systemd/system/zookeeper.service
rm -f $zookeeperF

sudo systemctl daemon-reload
sudo mkdir -p /var/zookeeper
sudo chown zk:zk -R /var/zookeeper

sudo systemctl start zookeeper

