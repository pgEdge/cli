#!/bin/bash

if [ "`id -u`" = "0" ]; then
   echo "****** Phase 1 running as root"
   if [ "`ps aux |grep sshd |grep -v grep`" = "" ]; then
      /usr/sbin/sshd

      mkdir -p /opt/pgedge
      chown -R pgedge /opt/pgedge

      mkdir ~pgedge/.ssh
      cd ~pgedge/.ssh
      ssh-keyscan localhost >>~pgedge/.ssh/known_hosts 2>/dev/null
      echo "StrictHostKeyChecking no" >/home/pgedge/.ssh/config
      unzip -o -P working /home/pgedge/pgedgekey.zip
      cp id_rsa.pub authorized_keys
      chown -R pgedge ~pgedge/.ssh
      chmod -R go-rwx ~pgedge/.ssh
      # scan the OTHER node in the cluster.
      if [ "$HOSTNAME" = "n1" ]; then
         ssh-keyscan pgedge1 >>~pgedge/.ssh/known_hosts 2>/dev/null
      elif [ "$HOSTNAME" = "n2" ]; then
         ssh-keyscan pgedge0 >>~pgedge/.ssh/known_hosts 2>/dev/null
      else
         echo "********** SSH-keyscan nothing for this node to do *******"
      fi
   fi

   # and then rerun this script as pgedge
   sudo -u pgedge $0
   exit
fi

#------ from here down we are user pgedge....
echo "****** Phase 2 running as pgedge"

cd /opt/pgedge/
export REPO=https://pgedge-download.s3.amazonaws.com/REPO
python3 -c "$(curl -fsSL $REPO/install.py)"
cd /opt/pgedge/pgedge
./nodectl install pgedge -U dbuser -P dbpassword -d demo


## Initializing pg16 #######################

if [ "$HOSTNAME" = "n1" ]; then
  source pg16/pg16.env
  ./nodectl spock node-create n1 "host=`hostname -I` user=pgedge dbname=demo" demo
  ./nodectl spock repset-create demo_replication_set demo
  PGEDGE1=`host n2 | awk '{print $NF}'`
  sleep 15
  echo "Setup to go from `hostname -I` to $PGEDGE1"
  ./nodectl spock sub-create sub_n1n2 "host=$PGEDGE1 port=5432 user=pgedge dbname=demo" demo


elif [ "$HOSTNAME" = "n2" ]; then
  source pg16/pg16.env
  ./nodectl spock node-create n2 "host=`hostname -I` user=pgedge dbname=demo" demo
  ./nodectl spock repset-create demo_replication_set demo
  PGEDGE0=`host n1 | awk '{print $NF}'`
  sleep 15
  echo "Setup to go from `hostname -I` to $PGEDGE0"
  ./nodectl spock sub-create sub_n2n1 "host=$PGEDGE0 port=5432 user=pgedge dbname=demo" demo

else
  echo "************nodectl: nothing for this node to do *******"
fi

# create the same table on both nodes
psql -d demo  -c "create table foobar(val1 bigint, val2 varchar(10)); "
psql -d demo  -c "alter table foobar add primary key (val1); "

# set it up to be replicated
./nodectl spock repset-add-table demo_replication_set foobar demo

if [ "$HOSTNAME" = "n1" ]; then
   ./nodectl spock sub-add-repset sub_n1n2 demo_replication_set demo
elif [ "$HOSTNAME" = "n2" ]; then
   ./nodectl spock sub-add-repset sub_n2n1 demo_replication_set demo
else
   echo "******** nodectl spock: nothing to do ******"
fi

psql demo -c "SELECT * FROM spock.node;"


# go forth and prosper.
#



