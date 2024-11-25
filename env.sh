hubV=24.10.7
hubVV=24.10-7

aceV=$hubV
kirkV=$hubV

bundle=pgedge
api=pgedge
ctlibsV=1.6

spock41V=4.1devel-2

spock40V=4.0.6-1
spock40V1=4.0.5-1

spock33V=3.3.6-1

lolorV=1.2-1
snwflkV=2.2-1

P17=17.2-1
P171=17.0-1

P16=16.6-1
P161=16.4-2

P15=15.10-1
P151=15.8-2

vectorV=0.8.0-1

bouncerV=1.23.1-1
catV=1.2.0
prompgexpV=0.15.0
backrestV=2.53.1-1
wal2jV=2.6.0-1

citusV=12.1.5-1
orafceV=4.13.4-1
v8V=3.2.3-1
setuserV=4.1.0-1
permissionsV=1.3-1

hypoV=1.4.1-1
timescaleV=2.17.0-1
profV=4.2.5-1
partmanV=5.0.1-1

hint15V=1.5.2-1
hint16V=1.6.1-1
hint17V=1.7.0-1

patroniV=3.2.2.2-1
etcdV=3.5.12-2

audit15V=1.7.0-1
audit16V=16.0-1
audit17V=17.0-1

postgisV=3.5.0-1

debuggerV=1.8-1
cronV=1.6.4-1

HUB="$PWD"
SRC="$HUB/src"
zipOut="off"
isENABLED=false

pg="postgres"

OS=`uname -s`
OS=${OS:0:7}

isEL8="False"
isEL9="False"
isEL="False"
if [ -f /etc/os-release ]; then
  PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
  if [ "$PLATFORM" == "el8" ]; then
    isEL="True"
    isEL8="True"
    isEL9="False"
  elif [ "$PLATFORM" == "el9" ]; then
    isEL="True"
    isEL8="False"
    isEL9="True"
  fi
fi

if [[ $OS == "Linux" ]]; then
  if [ `arch` == "aarch64" ]; then
    OS=arm
    outDir=a64
    outPlat=arm
  else
    OS=amd
    outDir=l64
    outPlat=amd
  fi
  sudo="sudo"
elif [[ $OS == "Darwin" ]]; then
  outDir=m64
  OS=osx
  outPlat=osx
  sudo=""
else
  echo "ERROR: '$OS' is not supported"
  return
fi

plat=$OS


fatalError () {
  echo "FATAL ERROR!  $1"
  exit 1
}


echoCmd () {
  echo "# $1"
  checkCmd "$1"
}


checkCmd () {
  $1
  rc=`echo $?`
  if [ ! "$rc" == "0" ]; then
    fatalError "Stopping Script"
  fi
}


setPGV () {
  if [ "$1" == "15" ]; then
    pgV=$P15
  elif [ "$1" == "16" ]; then
    pgV=$P16
  elif [ "$1" == "17" ]; then
    pgV=$P17
  else
    fatalError "Invalid PG version ($1)"
  fi
  pgMAJ=`echo "$pgV" | cut -d'.' -f1`
  pgMIN=`echo "$pgV" | cut -d'-' -f1 | cut -d'.' -f2`
  pgREV=`echo "$pgV" | cut -d'-' -f2`
}
