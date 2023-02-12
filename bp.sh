source env.sh 

## optional parms
comp="$1"

echo "########## Build POSIX Sandbox ##########"

outp="out/posix"

clusterDir=$outp/cluster
if [ -d $clusterDir ]; then
  $outp/$api local-cluster destroy all --verbose
fi

if [ -d $outp ]; then
  echo "Removing current '$outp' directory..."
  $outp/$api stop
  sleep 2
  sudo rm -rf $outp/data/*
  sudo rm -rf $outp
  sudo rm -rf /data
fi

sudo rm -rf /var/lib/pgbackrest

./startHTTP.sh
./build.sh -X posix -R

cd $outp

./$api set GLOBAL REPO http://localhost:8000
./$api info

if [ ! "$1" == "" ]; then
  ./$api install $comp
fi

