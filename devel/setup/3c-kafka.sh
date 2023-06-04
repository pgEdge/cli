#!/bin/bash
cd "$(dirname "$0")"

kafkaV=3.4.0
kafkaD=kafka_2.13-$kafkaV
kafkaF=$kafkaD.tgz
URL=https://dlcdn.apache.org/kafka

rm -rf $kafkaF
wget $URL/$kafkaV/$kafkaF
tar xzf $kafkaF

kdir=/usr/local/kafka
if [ -d "$kdir" ]; then
  ./remove-kafka
fi
sudo mv $kafkaD $kdir

cat <<EOT>> kafka.service
[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html

[Service]
Type=simple
Environment="JAVA_HOME=java_home"
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/kraft/server1.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh

[Install]
WantedBy=multi-user.target
EOT
sed -i "s|java_home|$java_home|g" kafka.service

sudo cp kafka.service     /etc/systemd/system/.
rm -rf $kafkaF

## KRAFT mode (zookeeper-less)
konfig_dir=/usr/local/kafka/config/kraft
cp $konfig_dir/server.properties $konfig_dir/server1.properties

my_uuid=`$kdir/bin/kafka-storage.sh random-uuid`
$kdir/bin/kafka-storage.sh format -t $my_uuid -c $konfig_dir/server1.properties

sudo systemctl daemon-reload
sudo systemctl start kafka

sleep 10
##/usr/local/kafka/bin/kafka-topics.sh --create --zookeeper 0.0.0.0:2181 --topic my-connect-configs --replication-factor 1 --partitions 10
/usr/local/kafka/bin/kafka-topics.sh --create --topic my-connect-configs --replication-factor 1 --partitions 10 --bootstrap-server localhost:9092

