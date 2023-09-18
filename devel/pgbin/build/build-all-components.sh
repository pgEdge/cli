#!/bin/bash
cd "$(dirname "$0")"

source versions.sh


function build {
  pgbin="--with-pgbin /opt/pgcomponent/pg$pgV"
  pgver="--with-pgver $3"
  src="$SRC/$1-$2.tar.gz"
  echo ""
  echo "###################################"
  cmd="./build-component.sh --build-$1 $src $pgbin $pgver $copyBin $4"
  echo "cmd=$cmd"
  $cmd
  rc=$?
}


################### MAINLINE #####################

pgV="$2"
copyBin="$3"
if [ "$copyBin" == "" ]; then
  copyBin="--no-copy-bin"
fi
if [[ "$pgV" < "11" ]] || [[ "$pgV" > "16" ]]; then
  echo  "ERROR: second parm must be 11 thru 16"
  exit 1
fi


## WIP ############################################

if [ "$1" == "vector" ]; then
  build vector $vectorFullV $2 vector
fi

if [ "$1" == "pljava" ]; then
  build pljava $pljavaFullV $2 pljava
fi

if [ "$1" == "plv8" ]; then
  build plv8 $plv8FullV $2 plv8
fi

if [ "$1" == "pgtop" ]; then
  build pgtop $pgtopFullV $2 pgtop
fi

if [ "$1" == "pldebugger" ]; then
  build pldebugger $debugFullV $2 pldebugger
fi

if [ "$1" == "hintplan" ]; then
  if [ "$pgV" == "16" ]; then
    build hintplan $hintplan16V $2 hintplan
  elif [ "$pgV" == "15" ]; then
    build hintplan $hintplan15V $2 hintplan
  fi
fi

if [ "$1" == "decoderbufs" ]; then
  build decoderbufs $decoderbufsFullV $2 decoderbufs
fi

if [ "$1" == "wal2json" ]; then
  build wal2json $wal2jsonFullV $2 wal2json
fi

if [ "$1" == "mongofdw" ]; then
  build mongofdw $mongofdwFullV $2 mongofdw
fi

if [ "$1" == "backrest" ]; then
  build backrest $backrestFullV $2 backrest
fi

if [ "$1" == "background" ]; then
  build background $bckgrndFullV $2 background
fi

if [ "$1" == "citus" ]; then
  build citus $citusFullV $2 citus
fi

if [ "$1" == "multicorn2" ]; then
  build multicorn2 $multicorn2FullV $2 multicorn2 
fi

if [ "$1" == "readonly" ]; then
  build readonly $readonlyFullV $2 readonly
fi

if [ "$1" == "foslots" ]; then
  build foslots $foslotsFullV $2 foslots
fi

if [ "$1" == "cron" ]; then
  build cron $cronFullV $2 cron
fi

if [ "$1" == "repack" ]; then
  build repack $repackFullV $2 repack
fi

if [ "$1" == "partman" ]; then
  build partman $partmanFullV $2 partman
fi

if [ "$1" == "bulkload" ]; then
  build bulkload $bulkloadFullV $2 bulkload
fi

if [ "$1" == "postgis" ]; then
  build postgis $postgisFullV $2 postgis  
fi

if [ "$1" == "audit" ]; then
  if [ "$pgV" == "16" ]; then
    build audit $auditFull16V $2 audit    
  elif [ "$pgV" == "15" ]; then
    build audit $auditFull15V $2 audit    
  fi
fi

if [ "$1" == "orafce" ]; then
  build orafce $orafceFullV $2 orafce
fi

if [ "$1" == "fixeddecimal" ]; then
  build fixeddecimal $fdFullV $2 fixeddecimal
fi

if [ "$1" == "curl" ]; then
  build curl $curlFullV $2 curl
fi

if [ "$1" == "hypopg" ]; then
  build hypopg $hypopgFullV $2 hypopg
fi

if [ "$1" == "plprofiler" ]; then
  build plprofiler $plProfilerFullVersion $2 profiler
fi

if [ "$1" == "timescaledb" ]; then
  build timescaledb $timescaledbFullV $2 timescale
fi

if [ "$1" == "spock31" ]; then
  build spock31 $spockFull31V $2  spock31
fi

if [ "$1" == "pool2" ]; then
  build pool2 $pool2FullV $2 pool2
fi

if [ "$1" == "pglogical" ]; then
  build pglogical $pgLogicalFullV $2 logical
fi

if [ "$1" == "anon" ]; then
  build anon $anonFullV $2 anon
fi

if [ "$1" == "ddlx" ]; then
  build ddlx $ddlxFullV $2 ddlx
fi

if [ "$1" == "bouncer" ]; then
  build bouncer $bouncerFullV $2 bouncer
fi

if [ "$1" == "mysqlfdw" ]; then
  build mysqlfdw $mysqlfdwFullV $2 mysqlfdw
fi

if [ "$1" == "oraclefdw" ]; then
  build oraclefdw $oraclefdwFullV $2 oraclefdw
fi

if [ "$1" == "logfdw" ]; then
  build logfdw $logfdwFullV $2 logfdw
fi

if [ "$1" == "tdsfdw" ]; then
  build tdsfdw $tdsfdwFullV $2 tdsfdw
fi

exit 0
