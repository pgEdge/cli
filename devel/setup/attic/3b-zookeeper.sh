
# Apache Zookeeper 

set -x

zookV=3.8.1

id -u zk > /dev/null 2>&1
rc=$?
if [ "$rc" == "1" ]; then
  sudo useradd zk -m
fi

sudo usermod -a -G wheel zk
sudo usermod --shell /bin/bash zk > /dev/null 2>&1

zookD=apache-zookeeper-$zookV-bin
zookF=$zookD.tar.gz
URL=https://dlcdn.apache.org/zookeeper
rm -f $zookF
wget $URL/zookeeper-$zookV/$zookF
tar xzf $zookF
rm $zookF

zkDir=/opt/zookeeper
sudo rm -rf $zkDir
sudo mv $zookD $zkDir

## CONFIG ##########################################
cat <<EOT>> zoo.cfg
tickTime=2000
dataDir=/var/zookeeper
clientPort=2181
admin.enableServer=false
EOT
sudo mv zoo.cfg $zkDir/conf/.

### SERVICE #####################################
cat <<EOT>> zookeeper.service
[Unit]
Description=Apache Zookeeper Server
Documentation=http://zookeeper.apache.org
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=forking                                                                    
User=zk
Group=zk
Environment="JAVA_HOME=/usr/lib/jvm/jre-17-openjdk"
ExecStart=/opt/zookeeper/bin/zkServer.sh  start  /opt/zookeeper/conf/zoo.cfg
ExecStop=/opt/zookeeper/bin/zkServer.sh   stop   /opt/zookeeper/conf/zoo.cfg
ExecReload=/opt/zookeeper/bin/zkServer.sh reload /opt/zookeeper/conf/zoo.cfg
WorkingDirectory=/var/zookeeper
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOT
sudo mv zookeeper.service /etc/systemd/system/.

## SYSTEMCTL #############################################
sudo systemctl daemon-reload
sudo mkdir -p /var/zookeeper
sudo chown zk:zk -R /var/zookeeper

sudo systemctl start zookeeper
