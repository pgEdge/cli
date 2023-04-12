
bundle=pgedge
api=nodectl
hubV=23.110

spockV=3.0.23-1
catV=1.0.0

P15=15.2-1
pgedgeV=15.2.1

P14=14.7-1
P13=13.10-1
P12=12.14-1
P11=11.19-1

goV=1.19.3
postgrestV=10.2.0-1
prompgexpV=0.11.1
nodejsV=18.12.1
backrestV=2.45-1
csvdiffV=1.4.0
pgdiffV=1.1
curlV=1.0.27-1
readonlyV=1.1.0-1

multicorn2V=2.4-1
esfdwV=0.11.2
bqfdwV=1.9

w2jV=2.4-1
citusV=11.2.0-1

oraclefdwV=2.5.0-1
inclV=21.6
orafceV=4.2.2-1
ora2pgV=23.1
v8V=3.1.2-1

fdV=1.1.0-1
anonV=1.1.0-1
ddlxV=0.17-1
hypoV=1.3.1-1
timescaleV=2.8.0-1
logicalV=2.4.2-1
profV=4.2-1
bulkloadV=3.1.19-1
partmanV=4.7.2-1
repackV=1.4.8-1
hintV=1.5.0-1

bouncerV=1.18.0-1
nginxV=1-1

#dbzV=1.8.1.Final
#apicV=2.2.0
#decbufsV=1.7.0-1

#zooV=3.7.0
#kfkV=3.1.0

##adminV=5.5
##omniV=2.17.0

audit14V=1.6.2-1
audit15V=1.7.0-1
postgisV=3.3.2-1

pljavaV=1.6.2-1
debuggerV=1.5-1
cronV=1.5.1-1

mysqlfdwV=2.8.0-1
mongofdwV=5.4.0-1
tdsfdwV=2.0.3-1
badgerV=11.6
patroniV=3.0

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
elif [[ $OS = "MINGW64" ]]; then
  outDir=w64
  OS=win
  sudo=""
else
  echo "ERROR: '$OS' is not supported"
  return
fi

plat=$OS
