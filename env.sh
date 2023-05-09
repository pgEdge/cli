
bundle=pgedge
api=nodectl
hubV=23.115

spock30V=3.0.23-1
spock31V=3.1dev3-1
catV=1.0.0

pgedgeV=2-1

P16=16devel-3
P15=15.3-1
P14=14.8-1
P13=13.11-1
P12=12.15-1
P11=11.20-1

goV=1.19.3
postgrestV=10.0.2-1
prompgexpV=0.11.1
nodejsV=18.12.1
backrestV=2.45-1
csvdiffV=1.4.0
pgdiffV=1.1
curlV=1.0.27-1
readonlyV=1.1.0-1
foslotsV=1a-1

multicorn2V=2.4-1
esfdwV=0.11.2
bqfdwV=1.9

w2jV=2.4-1
citusV=11.2.0-1

oraclefdwV=2.5.0-1
inclV=21.6
orafceV=4.2.5-1
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
partmanV=4.7.3-1
repackV=1.4.8-1
hintV=1.5.0-1

bouncerV=1.18.0-1
nginxV=1-1

#dbzV=1.8.1.Final
#apicV=2.2.0
#decbufsV=1.7.0-1

zookV=3.7.1
#kfkV=3.1.0
patroniV=3.0

##adminV=5.5
##omniV=2.17.0

audit14V=1.6.2-1
audit15V=1.7.0-1
postgisV=3.3.2-1

pljavaV=1.6.2-1
debuggerV=1.5-1
cronV=1.5.2-1

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
