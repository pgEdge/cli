
bundle=pgedge
api=pgedge
hubV=24.7.6
ctlibsV=1.4

spock40V=4.0.1-1
spock33V=3.3.5-1

lolorV=1.2-1
foslotsV=1a-1
snwflkV=2.2-1

P17=17beta3-1
P16=16.4-1
P15=15.8-1
P14=14.13-1
##P13=13.15-3
##P12=12.19-3

vectorV=0.7.4-1
bouncerV=1.23.1-1
catV=1.1.1
firwldV=1.2
adminV=8.x
##prestV=1.4.2
##postgrestV=12.0.2-1
prompgexpV=0.15.0
backrestV=2.53-1
wal2jV=2.6.0-1

##curlV=2.2.2-1
citusV=12.1.5-1
orafceV=4.10.3-1
v8V=3.2.2-1
setuserV=4.0.1-1
permissionsV=1.3-1

## oraclefdwV=2.6.0-1
## inclV=21.6
## ora2pgV=23.1

hypoV=1.4.1-1
timescaleV=2.16.1-1
profV=4.2.5-1
bulkloadV=3.1.19-1
partmanV=5.0.1-1

hint15V=1.5.1-1
hint16V=1.6.0-1

patroniV=3.2.2.1-1
etcdV=3.5.12-2

audit15V=1.7.0-1
audit16V=16.0-1

postgisV=3.4.2-1

pljavaV=1.6.4-1
debuggerV=1.6-1
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
    ##outPlat=arm9
    outPlat=arm
  else
    OS=amd
    outDir=l64
    outPlat=amd
    ##if [ "$isEL8" == "True" ]; then
    ##  outPlat=el8
    ##else 
    ##  outPlat=el9
    ##fi
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
  if [ "$1" == "12" ]; then
    pgV=$P12
  elif [ "$1" == "13" ]; then
    pgV=$P13
  elif [ "$1" == "14" ]; then
    pgV=$P14
  elif [ "$1" == "15" ]; then
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
