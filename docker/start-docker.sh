#/!/bin/bash

# store the pgedge files in /tmp
mkdir -p /tmp/tmp/pgedge-data /tmp/tmp/pgedge-logs


export DEPEND=""
export PUBLISH="-p 23432:5432"
export IMAGE=pgedge
export HOSTNAME=pgedge
export NAME=pgedge2
export SSH=
export DAEMON=
export _MAX_MAP='-e MAX_MAP_COUNT=262144'

# first check if the image is built yet
TEST=`docker images $IMAGE`
if [ "$TEST" = "" ]; then
   echo "Image needs to be built."
   docker build --tag $IMAGE
   RC=$?
   if [ "$RC" != "0" ] ;then
     echo "Filed to build - $RC"
     exit
   fi
fi

docker run -it \
    -h $HOSTNAME \
    --restart=always \
    $PUBLISH \
    --name $NAME $IMAGE $SHELL

