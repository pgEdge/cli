#!/bin/bash

if [ ! -d /opt/pgedge/pgedge/pg16 ];
then
  ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
  cp ~/.ssh/id_ed25519.pub ~/ssh-keys/$HOSTNAME.pub
  cat ~/ssh-keys/*.pub >> ~/.ssh/authorized_keys

  sudo mkdir -p /opt/pgedge/ 
  sudo chown -R pgedge /opt/pgedge
  cd /opt/pgedge
  python3 -c "$(curl -fsSL $REPO/install.py)"
  cd pgedge
  ./nodectl install pgedge -U $DBUSER -P $DBPASSWD -d $DBNAME

  source pg16/pg16.env
  ./nodectl spock node-create $HOSTNAME "host=`hostname -I` user=pgedge dbname=$DBNAME" $DBNAME
  ./nodectl spock repset-create "$DBNAME"_replication_set $DBNAME
  PGEDGE=`host $PEER_HOSTNAME | awk '{print $NF}'`

  while ! nc -z $PEER_HOSTNAME $DBPORT; do   
    sleep 0.1
  done

  while :
  do
    mapfile -t node_array < <(psql -A -t $DBNAME -h $PEER_HOSTNAME -c "SELECT node_name FROM spock.node;")
    for element in "${node_array[@]}"; do
      if [[ "$element" == "$PEER_HOSTNAME" ]]; then
          break 2
      fi
    done
    sleep 1
    echo "Waiting for spock.node ..."
  done

  echo "Setup to go from `hostname -I` to $PGEDGE"
  ./nodectl spock sub-create sub_$HOSTNAME$PEER_HOSTNAME "host=$PGEDGE port=5432 user=pgedge dbname=$DBNAME" $DBNAME

  # create the same table on both nodes
  psql -d $DBNAME -c "create table foobar(val1 bigint, val2 varchar(10)); "
  psql -d $DBNAME -c "alter table foobar add primary key (val1); "

  # set it up to be replicated
  ./nodectl spock repset-add-table "$DBNAME"_replication_set foobar $DBNAME
  ./nodectl spock sub-add-repset sub_$HOSTNAME$PEER_HOSTNAME "$DBNAME"_replication_set $DBNAME

  psql $DBNAME -c "SELECT * FROM spock.node;"

else
  cd /opt/pgedge/pgedge
  ./nodectl start
fi

# XXX: Use supervisord
tail -f /dev/null
