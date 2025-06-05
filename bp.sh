source env.sh 

## optional parms
comp="$1"

echo "########## Build POSIX Sandbox ##########"

outp="out/posix"

clusterDir=$outp/cluster
if [ -d $clusterDir ]; then
  echo "Removing local clusters..."
  $outp/$api localhost cluster-destroy all
fi

if [ -d $outp ]; then
  echo "Removing current '$outp' directory..."
  $outp/$api stop
  sleep 2
  sudo rm -rf $outp/data/*
  sudo rm -rf $outp
fi

./devel/startHTTP.sh

echo "Waiting for Python HTTP server to start..."
while ! ss -tln | grep -q ':8000'; do 
 sleep 1; 
done


echo "HTTP server is up!"

./build.sh -X posix -R
cd $outp

./$api set GLOBAL REPO http://localhost:8000
./$api info --silent
if [ `arch` == "i386" ]; then
  echo "Skipping CTLIBS for `arch`"
else
  if [ ! -f $OUT/ctlibs-py3.9-amd.tgz ]; then
    cp -pv $IN/ctlibs/*.tgz $OUT/.
  fi
  ./$api install ctlibs
fi

