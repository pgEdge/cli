source env.sh 

## optional parms
comp="$1"

echo "########## Build POSIX Sandbox ##########"

outp="out/posix"

if [ -d $outp ]; then
  echo "Removing current '$outp' directory..."
  $outp/$api stop
  sleep 2
  $sudo rm -rf $outp
fi

./startHTTP.sh
./build.sh -X posix -R

cd $outp

./$api set GLOBAL REPO http://localhost:8000
./$api info

if [ ! "$1" == "" ]; then
  ./$api install $comp
fi

