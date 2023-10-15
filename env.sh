
bundle=pgedge
api=nodectl
hubV=24.001

spock32V=3.2dev2-1
spock31V=3.1.7-1
catV=1.1.1
ncdV=1.0
foslotsV=1a-1

pgedgeV=2-5

P17=17devel-1
P16=16.0-1
P15=15.4-2
P14=14.9-1
P13=13.12-1
P12=12.16-1

postgrestV=11.2.0-1
prompgexpV=0.11.1
backrestV=2.47-1
csvdiffV=1.4.0
curlV=2.1.1-1
readonlyV=1.1.0-1

multicorn2V=2.4-1
esfdwV=0.11.2
bqfdwV=1.9

citusV=11.2.0-1
vectorV=0.5.0-1

oraclefdwV=2.6.0-1
inclV=21.6
orafceV=4.5.0-1
ora2pgV=23.1
v8V=3.2.0-1

anonV=1.1.0-1
ddlxV=0.17-1
hypoV=1.4.0-1
timescaleV=2.11.2-1
logicalV=2.4.3-1
profV=4.2.4-1
bulkloadV=3.1.19-1
partmanV=4.7.4-1
repackV=1.4.8-1

hint15V=1.5.1-1
hint16V=1.6.0-1

patroniV=3.1.2.1
etcdV=3.5.9

audit15V=1.7.0-1
audit16V=16.0-1

postgisV=3.4.0-1

pljavaV=1.6.4-1
debuggerV=1.5-1
cronV=1.6.0-1

#mysqlfdwV=2.8.0-1
#mongofdwV=5.4.0-1
#tdsfdwV=2.0.3-1
#badgerV=11.6

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
