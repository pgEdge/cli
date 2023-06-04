
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
rm -rf $zookF
wget $URL/zookeeper-$zookV/$zookF
tar xzf $zookF

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

## LOGGING ########################################
cat <<EOT>> log4j.properties
# Copyright 2012 The Apache Software Foundation

# Define some default values that can be overridden by system properties
zookeeper.root.logger=INFO, CONSOLE

zookeeper.console.threshold=INFO

zookeeper.log.dir=.
zookeeper.log.file=zookeeper.log
zookeeper.log.threshold=INFO
zookeeper.log.maxfilesize=256MB
zookeeper.log.maxbackupindex=20

zookeeper.tracelog.dir=${zookeeper.log.dir}
zookeeper.tracelog.file=zookeeper_trace.log

log4j.rootLogger=${zookeeper.root.logger}

#
# console
# Add "console" to rootlogger above if you want to use this 
#
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.CONSOLE.Threshold=${zookeeper.console.threshold}
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

#
# Add ROLLINGFILE to rootLogger to get log file output
#
log4j.appender.ROLLINGFILE=org.apache.log4j.RollingFileAppender
log4j.appender.ROLLINGFILE.Threshold=${zookeeper.log.threshold}
log4j.appender.ROLLINGFILE.File=${zookeeper.log.dir}/${zookeeper.log.file}
log4j.appender.ROLLINGFILE.MaxFileSize=${zookeeper.log.maxfilesize}
log4j.appender.ROLLINGFILE.MaxBackupIndex=${zookeeper.log.maxbackupindex}
log4j.appender.ROLLINGFILE.layout=org.apache.log4j.PatternLayout
log4j.appender.ROLLINGFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

#
# Add TRACEFILE to rootLogger to get log file output
#    Log TRACE level and above messages to a log file
#
log4j.appender.TRACEFILE=org.apache.log4j.FileAppender
log4j.appender.TRACEFILE.Threshold=TRACE
log4j.appender.TRACEFILE.File=${zookeeper.tracelog.dir}/${zookeeper.tracelog.file}

log4j.appender.TRACEFILE.layout=org.apache.log4j.PatternLayout
### Notice we are including log4j's NDC here (%x)
log4j.appender.TRACEFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L][%x] - %m%n
#
# zk audit logging
#
zookeeper.auditlog.file=zookeeper_audit.log
zookeeper.auditlog.threshold=INFO
audit.logger=INFO, RFAAUDIT
log4j.logger.org.apache.zookeeper.audit.Log4jAuditLogger=${audit.logger}
log4j.additivity.org.apache.zookeeper.audit.Log4jAuditLogger=false
log4j.appender.RFAAUDIT=org.apache.log4j.RollingFileAppender
log4j.appender.RFAAUDIT.File=${zookeeper.log.dir}/${zookeeper.auditlog.file}
log4j.appender.RFAAUDIT.layout=org.apache.log4j.PatternLayout
log4j.appender.RFAAUDIT.layout.ConversionPattern=%d{ISO8601} %p %c{2}: %m%n
log4j.appender.RFAAUDIT.Threshold=${zookeeper.auditlog.threshold}

# Max log file size of 10MB
log4j.appender.RFAAUDIT.MaxFileSize=10MB
log4j.appender.RFAAUDIT.MaxBackupIndex=10
EOT
sudo mv log4j.properties $zkDir/conf/.
sudo chown zk:zk -R $zkDir

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
