#!/bin/bash

spockFull31V=3.1.4
spockBuild31V=1

pg16V=16beta3
pg16BuildV=2

pg15V=15.4
pg15BuildV=2

pg14V=14.9
pg14BuildV=1

pg13V=13.12
pg13BuildV=1

pg12V=12.16
pg12BuildV=1

pg11V=11.21
pg11BuildV=1

readonlyFullV=1.1.0
readonlyShortV=
readonlyBuildV=1

decoderbufsFullV=1.7.0
decoderbufsShortV=
decoderbufsBuildV=1

curlFullV=2.1.1
curlShortV=
curlBuildV=1

odbcFullV=13.01
odbcShortV=
odbcBuildV=1

backrestFullV=2.47
backrestShortV=
backrestBuildV=1

multicorn2FullV=2.4
multicorn2ShortV=
multicorn2BuildV=1

citusFullV=11.2.0
citusShortV=
citusBuildV=1

vectorFullV=0.4.4
vectorShortV=
vectorBuildV=1

hypopgFullV=1.4.0
hypopgShortV=
hypopgBuildV=1

postgisFullV=3.3.4
postgisShortV=
postgisBuildV=1

orafceFullV=4.3.0
orafceShortV=
orafceBuildV=1

oraclefdwFullV=2.5.0
oraclefdwShortV=
oraclefdwBuildV=1

logfdwFullV=1.4
logfdwShortV=
logfdwBuildV=1

tdsfdwFullV=2.0.3
tdsfdwShortV=
tdsfdwBuildV=1

mysqlfdwFullV=2.8.0
mysqlfdwShortV=
mysqlfdwBuildV=1

mongofdwFullV=5.4.0
mongofdwShortV=
mongofdwBuildV=1

plProfilerFullVersion=4.2.2
plProfilerShortVersion=
plprofilerBuildV=1

plv8FullV=3.2.0
plv8ShortV=
plv8BuildV=1

debugFullV=1.5
debugShortV=
debugBuildV=1

anonFullV=1.1.0
anonShortV=
anonBuildV=1

ddlxFullV=0.17
ddlxShortV=
ddlxBuildV=1

auditFull15V=1.7.0
auditShortV=
auditBuildV=1

pljavaFullV=1.6.4
pljavaShortV=
pljavaBuildV=1

bulkloadFullV=3.1.19
bulkloadShortV=
bulkloadBuildV=1

pgLogicalFullV=2.4.3
pgLogicalShortV=
pgLogicalBuildV=1

repackFullV=1.4.8
repackShortV=
repackBuildV=1

partmanFullV=4.7.3
partmanShortV=
partmanBuildV=1

hintplanFullV=1.5.0
hintplanShortV=
hintplanBuildV=1

timescaledbFullV=2.11.0
timescaledbShortV=
timescaledbBuildV=1

cronFullV=1.5.2
cronShortV=
cronBuildV=1

PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
if [ "$PLATFORM" == "el8" ]; then
  isEL=yes
  isEL8=yes
  isEL9=no
elif [ "$PLATFORM" == "el9" ]; then
  isEL=yes
  isEL8=no
  isEL9=yes
else
  isEL=no
  isEL8=no
  isEL9=no
fi

ARCH=`arch`
OS=`uname -s`
OS=${OS:0:7}
if [[ "$OS" == "Linux" ]]; then
  CORES=`egrep -c 'processor([[:space:]]+):.*' /proc/cpuinfo`
  if [ "$CORES" -gt "24" ]; then
    CORES=24
  fi
  if [[ "$ARCH" == "aarch64" ]]; then
    OS=arm
    if [[ "$isEL9" == "yes" ]]; then
      OS=arm9
    fi
  else
    if [[ "$isEL8" == "yes" ]]; then
      OS=el8
    elif [[ "$isEL9" == "yes" ]]; then
      OS=el9
    else
      OS=amd
    fi
  fi
elif [[ "$OS" == "Darwin" ]]; then
  CORES=`/usr/sbin/sysctl hw.physicalcpu | awk '{print $2}'`
  OS="osx"
else
  echo "Think again. :-)"
  exit 1
fi

