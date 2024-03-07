
bundle=pgedge
api=pgedge
hubV=24.2.6
ctlibsV=1.2

spock33V=3.3dev2-1
spock32V=3.2.8-1

foslotsV=1a-1
snwflkV=1.2-1
vectorV=0.6.1-1

grp_pgeV=2.12

P17=17devel-1
P16=16.2-3
P15=15.6-3
P14=14.11-1
P13=13.14-1
P12=12.18-1

catV=1.1.1
firwldV=1.2
adminV=8.x
prestV=1.4.2
postgrestV=12.0.2-1
prompgexpV=0.15.0-1
backrestV=2.50-2
readonlyV=1.1.1-1
wal2jV=2.5.1-1

curlV=2.2.2-1
citusV=12.1.2-1

oraclefdwV=2.6.0-1
inclV=21.6
orafceV=4.9.2-1
ora2pgV=23.1
v8V=3.2.2-1

hypoV=1.4.0-1
timescaleV=2.13.1-1
logicalV=2.4.4-1
profV=4.2.4-1
bulkloadV=3.1.19-1
partmanV=5.0.1-1
repackV=1.4.8-1

hint15V=1.5.1-1
hint16V=1.6.0-1

patroniV=3.2.1-1
etcdV=3.5.12

audit15V=1.7.0-1
audit16V=16.0-1

postgisV=3.4.2-1

pljavaV=1.6.4-1
debuggerV=1.6-1
cronV=1.6.2-1

HUB="$PWD"
SRC="$HUB/src"
zipOut="off"
isENABLED=false

pg="postgres"

OS=`uname -s`
OS=${OS:0:7}

if [[ $OS == "Linux" ]]; then
  if [ `arch` == "aarch64" ]; then
    OS=arm
    outDir=a64
  else
    OS=amd;
    outDir=l64
  fi
  sudo="sudo"
elif [[ $OS == "Darwin" ]]; then
  outDir=m64
  OS=osx;
  sudo=""
else
  echo "ERROR: '$OS' is not supported"
  return
fi

plat=$OS
