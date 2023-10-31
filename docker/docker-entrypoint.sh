#!/bin/bash

ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
cp ~/.ssh/id_ed25519.pub ~/ssh-keys/$HOSTNAME.pub
cat ~/ssh-keys/*.pub >> ~/.ssh/authorized_keys

cd /opt/pgedge/
python3 -c "$(curl -fsSL $REPO/install.py)"
cd pgedge
./nodectl install pgedge -U dbuser -P dbpassword -d demo


## Initializing pg16 #######################

source pg16/pg16.env
./nodectl spock node-create $HOSTNAME "host=`hostname -I` user=pgedge dbname=demo" demo
./nodectl spock repset-create demo_replication_set demo
PGEDGE=`host $PEER_HOSTNAME | awk '{print $NF}'`
sleep 15
echo "Setup to go from `hostname -I` to $PGEDGE"
./nodectl spock sub-create sub_n1n2 "host=$PGEDGE port=5432 user=pgedge dbname=demo" demo

# create the same table on both nodes
psql -d demo  -c "create table foobar(val1 bigint, val2 varchar(10)); "
psql -d demo  -c "alter table foobar add primary key (val1); "

# set it up to be replicated
./nodectl spock repset-add-table demo_replication_set foobar demo

./nodectl spock sub-add-repset sub_$HOSTNAME$PEER_HOSTNAME demo_replication_set demo

psql demo -c "SELECT * FROM spock.node;"

tail -f /dev/null
