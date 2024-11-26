#!/bin/bash

lolorV=1.2
lolorBldV=1

spock40V=4.0.1
spockBld40V=1

spock33V=3.3.6
spockBld33V=1

pg17V=17rc1
pg17BuildV=1

pg16V=16.4
pg16BuildV=1

pg15V=15.8
pg15BuildV=1

pg14V=14.13
pg14BuildV=1

snwflkV=2.2
snwflkBldV=1

wal2jV=2.6.0
wal2jBldV=1

bouncerV=1.23.1
bouncerBldV=1

decoderbufsFullV=1.7.0
decoderbufsShortV=
decoderbufsBuildV=1

backrestFullV=2.53
backrestShortV=
backrestBuildV=1

multicornFullV=3.0beta1
multicornShortV=
multicornBuildV=1

citusFullV=12.1.5
citusShortV=
citusBuildV=1

vectorFullV=0.7.4
vectorShortV=
vectorBuildV=1

hypopgFullV=1.4.1
hypopgShortV=
hypopgBuildV=1

postgisFullV=3.4.3
postgisShortV=
postgisBuildV=1

orafceFullV=4.10.3
orafceShortV=
orafceBuildV=1

sqlitefdwFullV=2.4.0
sqlitefdwShortV=
sqlitefdwBuildV=1

plProfilerFullVersion=4.2.5
plProfilerShortVersion=
plprofilerBuildV=1

plv8FullV=3.2.2
plv8ShortV=
plv8BuildV=1

debugFullV=1.8
debugShortV=
debugBuildV=1

auditFull15V=1.7.0
auditFull16V=16.0
auditShortV=
auditBuildV=1

setuserFullV=4.0.1
setuserShortV=
setuserBuildV=1

permissionsFullV=1.3
permissionsShortV=
permissionsBuildV=1

pljavaFullV=1.6.6
pljavaShortV=
pljavaBuildV=1

partmanFullV=5.0.1
partmanShortV=
partmanBuildV=1

hintplan17V=1.7.0
hintplan16V=1.6.1
hintplan15V=1.5.2
hintplanShortV=
hintplanBuildV=1

timescaledbFullV=2.16.1
timescaledbShortV=
timescaledbBuildV=1

cronFullV=1.6.4
cronShortV=
cronBuildV=1

isEL=no
isEL8=no
isEL9=no
isEL10=no

if [ -f /etc/os-release ]; then
  PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
  if [ "$PLATFORM" == "el8" ]; then
    isEL=yes
    isEL8=yes
  elif [ "$PLATFORM" == "el9" ]; then
    isEL=yes
    isEL9=yes
  elif [ "$PLATFORM" == "f40" ]; then
    isEL=yes
    isEL10=yes 
  fi
fi

ARCH=`arch`
OS=`uname -s`
OS=${OS:0:7}
if [[ "$OS" == "Linux" ]]; then
  CORES=`egrep -c 'processor([[:space:]]+):.*' /proc/cpuinfo`
  if [ "$CORES" -gt "16" ]; then
    CORES=16
  fi
  if [[ "$ARCH" == "aarch64" ]]; then
    OS=arm
  else
    OS=amd
  fi
elif [[ "$OS" == "Darwin" ]]; then
  CORES=`/usr/sbin/sysctl hw.physicalcpu | awk '{print $2}'`
  OS="osx"
else
  echo "Think again. :-)"
  exit 1
fi

