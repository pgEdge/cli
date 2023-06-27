#!/bin/bash
cd "$(dirname "$0")"

source env.sh

if [ "x$REPO" == "x" ]; then
  repo="http://localhost"
else
  repo="$REPO"
fi

PYTHON=python3

if [ "$OUT" == "" ]; then
  echo "ERROR: Environment is not set"
  exit 1
fi


printUsageMessage () {
  echo "#-------------------------------------------------------------------#"
  echo "#                Copyright (c) 2022-2023 PGEDGE                     #"
  echo "#-------------------------------------------------------------------#"
  echo "# -p $P16 $P15 $P14 $P13 $P12 $P11"
  echo "# -b hub-$hubV"
  echo "#-------------------------------------------------------------------#"
}


fatalError () {
  echo "FATAL ERROR!  $1"
  if [ "$2" == "u" ]; then
    printUsageMessage
  fi
  echo
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


myReplace () {
  oldVal="$1"
  newVal="$2"
  fileName="$3"

  if [ ! -f "$fileName" ]; then
    echo "ERROR: Invalid file name - $fileName"
    return 1
  fi

  if [ `uname` == "Darwin" ]; then
    sed -i "" "s#$oldVal#$newVal#g" "$fileName"
  else
    sed -i "s#$oldVal#$newVal#g" "$fileName"
  fi
}

## write Setting row to SETTINGS config table
writeSettRow() {
  pSection="$1"
  pKey="$2"
  pValue="$3"
  pVerbose="$4"
  dbLocal="$out/conf/db_local.db"
  cmdPy="$PYTHON $HUB/src/conf/insert_setting.py"
  $cmdPy "$dbLocal"  "$pSection" "$pKey" "$pValue"
  if [ "$pVerbose" == "-v" ]; then
    echo "$pKey = $pValue"
  fi
}


## write Component row to COMPONENTS config table
writeCompRow() {
  pComp="$1"
  pProj="$2"
  pVer="$3"
  pPlat="$4"
  pPort="$5"
  pStatus="$6"
  pStageDir="$7"

  if [ ! "$pStageDir" == "nil" ]; then
    echo "#"
  fi

  if [ "$pStatus" == "NotInstalled" ] && [ "$isENABLED" == "true" ]; then
    pStatus="Enabled"
  fi

  if [ ! "$pStatus" == "Enabled" ]; then
    return
  fi

  dbLocal="$out/conf/db_local.db"
  cmdPy="$PYTHON $HUB/src/conf/insert_component.py"
  $cmdPy "$dbLocal"  "$pComp" "$pProj" "$pVer" "$pPlat" "$pPort" "$pStatus"
}


initDir () {
  pComponent=$1
  pProject=$2
  pPreNum=$3
  pExt=$4
  pStageSubDir=$5
  pStatus="$6"
  pPort="$7"
  pParent="$8"

  if [ "$pStatus" == "" ]; then
    pStatus="NotInstalled"
  fi

  if [ "$pStatus" == "NotInstalled" ] && [ "$isENABLED" == "true" ]; then
    pStatus="Enabled"
  fi

  if [ "$pStatus" == "NotInstalled" ] && [ ! "$zipOut" == "off" ]; then
     if [ "$pExt" == "" ]; then
       fileNm=$OUT/$pComponent-$pPreNum.tar.bz2
     else
       fileNm=$OUT/$pComponent-$pPreNum-$pExt.tar.bz2
     fi
     if [ -f "$fileNm" ]; then
       return
     fi
  fi

  osName=`uname`
  if [ "$osName" == "Darwin" ]; then
    cpCmd="cp -r"
  else
    cpCmd="cp -Lr"
  fi

  writeCompRow "$pComponent" "$pProject" "$pPreNum" "$pExt" "$pPort" "$pStatus" "nil"

  if [ "$pExt" == "" ]; then
    pCompNum=$pPreNum
  else
    pCompNum=$pPreNum-$pExt
  fi

  if [ "$pParent" == "Y" ]; then
    myOrigDir=$pComponent
  else
    myOrigDir=$pComponent-$pCompNum
  fi
  myOrigFile=$myOrigDir.tar.bz2

  if [ "$pStageSubDir" == "nil" ]; then
    thisDir=$IN
  else
    thisDir=$IN/$pStageSubDir
  fi
 
  if [ ! -d "$thisDir/$myOrigDir" ]; then
    origFile=$thisDir/$myOrigFile
    if [ -f $origFile ]; then
      checkCmd "tar -xf $origFile"      
      ## pbzip2 -dc $origFile | tar x
      rc=`echo $?`
      if [ $rc -ne 0 ]; then
        fatalError "can't unzip"
      fi
    else
      fatalError "Missing input file: $origFile"
    fi
  fi

  myNewDir=$pComponent
  if [ "$pParent" == "nil" ]; then
     mv $myOrigDir $myNewDir
  fi

  if [ -d "$SRC/$pComponent" ]; then
    $cpCmd $SRC/$pComponent/*  $myNewDir/.
  fi

  copy-pgXX "orafce"
  copy-pgXX "spock31"
  copy-pgXX "curl"
  copy-pgXX "pglogical"
  copy-pgXX "anon"
  copy-pgXX "plprofiler"
  copy-pgXX "pldebugger"
  copy-pgXX "partman"
  copy-pgXX "repack"
  copy-pgXX "bulkload"
  copy-pgXX "audit"   
  copy-pgXX "postgis"   
  ##copy-pgXX "mysqlfdw"  
  ##copy-pgXX "apicurio"
  copy-pgXX "mongofdw"  
  copy-pgXX "decoderbufs"  
  ##copy-pgXX "oraclefdw"  
  ##copy-pgXX "tdsfdw"  
  copy-pgXX "cron"
  copy-pgXX "readonly"
  ##copy-pgXX "foslots"
  copy-pgXX "citus"
  ##copy-pgXX "multicorn2"
  ##copy-pgXX "esfdw"
  ##copy-pgXX "bqfdw"
  copy-pgXX "pljava"
  copy-pgXX "plv8"
  copy-pgXX "hintplan"
  ##copy-pgXX "nginx"
  copy-pgXX "timescaledb"
  copy-pgXX "hypopg"

  ## ARCHIVED #########
  ##copy-pgXX "fixeddecimal"
  ##copy-pgXX "cassandrafdw"
  ##copy-pgXX "hivefdw"
  ##copy-pgXX "wal2json"  

  if [ -f $myNewDir/LICENSE.TXT ]; then
    mv $myNewDir/LICENSE.TXT $myNewDir/$pComponent-LICENSE.TXT
  fi

  if [ -f $myNewDir/src.tar.gz ]; then
    mv $myNewDir/src.tar.gz $myNewDir/$pComponent-src.tar.gz
  fi

  ##rm -f $myNewDir/*INSTALL*
  rm -f $myNewDir/logs/*

  rm -rf $myNewDir/manual

  rm -rf $myNewdir/build*
  rm -rf $myNewDir/.git*
}


copy-pgXX () {
  if [ "$pComponent" == "$1-pg$pgM" ]; then
    checkCmd "cp -r $SRC/$1-pgXX/* $myNewDir/."

    checkCmd "mv $myNewDir/install-$1-pgXX.py $myNewDir/install-$1-pg$pgM.py"
    myReplace "pgXX" "pg$pgM" "$myNewDir/install-$1-pg$pgM.py"

    if [ -f $myNewDir/remove-$1-pgXX.py ]; then
      checkCmd "mv $myNewDir/remove-$1-pgXX.py $myNewDir/remove-$1-pg$pgM.py"
      myReplace "pgXX" "pg$pgM" "$myNewDir/remove-$1-pg$pgM.py"
    fi
  fi
}


zipDir () {
  pComponent="$1"
  pNum="$2"
  pPlat="$3"
  pStatus="$4"

  if [ "$zipOut" == "off" ]; then
    return
  fi

  if [ "$pPlat" == "" ]; then
    baseName=$pComponent-$pNum
  else
    baseName=$pComponent-$pNum-$pPlat
  fi
  myTarball=$baseName.tar.bz2
  myChecksum=$myTarball.sha512

  if [ ! -f "$OUT/$myTarball" ] && [ ! -f "$OUT/$myChecksum" ]; then
    echo "COMPONENT = '$baseName' '$pStatus'"
    options=""
    if [ "$osName" == "Linux" ]; then
      options="--owner=0 --group=0"
    fi
    checkCmd "tar $options -cjf $myTarball $pComponent"
    writeFileChecksum $myTarball
  fi

  if [ "$pStatus"  == "NotInstalled" ]; then
    rm -rf $pComponent
  fi
}


## move file to output directory and write a checksum file with it
writeFileChecksum () {
  pFile=$1
  sha512=`openssl dgst -sha512 $pFile | awk '{print $2}'`
  checkCmd "mv $pFile $OUT/."
  echo "$sha512  $pFile" > $OUT/$pFile.sha512
}


finalizeOutput () {
  writeCompRow "hub"  "hub" "$hubV" "" "0" "Enabled" "nil"
  checkCmd "cp -r $NC/docker ."
  checkCmd "cp -r $SRC/hub ."
  checkCmd "mkdir -p hub/scripts"
  checkCmd "cp -r $CLI/* hub/scripts/."
  checkCmd "cp -r $CLI/../doc hub/."
  checkCmd "cp $CLI/../README.md  hub/doc/."
  checkCmd "rm -f hub/scripts/*.pyc"
  zipDir "hub" "$hubV" "" "Enabled"

  checkCmd "cp conf/$verSQL ."
  writeFileChecksum "$verSQL"

  checkCmd "cd $HUB"

  if [ ! "$zipOut" == "off" ] &&  [ ! "$zipOut" == "" ]; then
    zipExtension="tar.bz2"
    options=""
    if [ "$osName" == "Linux" ]; then
      options="--owner=0 --group=0"
    fi
    zipCommand="tar $options -cjf"
    zipCompressProg=""

    zipOutFile="$zipOut-$NUM-$plat.$zipExtension"
    if [ "$plat" == "posix" ]; then
      zipOutFile="$zipOut-$NUM.$zipExtension"
    fi

    if [ "$platx" == "posix" ]; then
      if [ ! -f $OUT/$zipOutFile ]; then
        echo "OUTFILE = '$zipOutFile'"
        checkCmd "cd out"
        checkCmd "mv $outDir $bundle"
        outDir=$bundle
        checkCmd "$zipCommand $zipOutFile $zipCompressProg $outDir"
        writeFileChecksum "$zipOutFile"
        checkCmd "cd .."
      fi
    fi
  fi
}


copyReplaceScript() {
  script=$1
  comp=$2
  checkCmd "cp $pgXX/$script-pgXX.py  $newDir/$script-$comp.py"
  myReplace "pgXX" "$comp" "$comp/$script-$comp.py"
}


supplementalPG () {
  newDir=$1
  pgXX=$SRC/pgXX

  checkCmd "mkdir $newDir/init"

  copyReplaceScript "install"  "$newDir"
  copyReplaceScript "start"    "$newDir"
  copyReplaceScript "stop"     "$newDir"
  copyReplaceScript "init"     "$newDir"
  copyReplaceScript "config"   "$newDir"
  copyReplaceScript "reload"   "$newDir"
  copyReplaceScript "activity" "$newDir"
  copyReplaceScript "remove"   "$newDir"

  checkCmd "cp $pgXX/*.sh         $newDir/"
  checkCmd "cp $pgXX/run-pgctl.py $newDir/"
  myReplace "pgXX" "$comp" "$newDir/run-pgctl.py"

  checkCmd "cp $pgXX/pg_hba.conf.nix  $newDir/"

  checkCmd "chmod 755 $newDir/bin/*"
  chmod 755 $newDir/lib/* 2>/dev/null
}


initC () {
  status="$6"
  if [ "$status" == "" ]; then
    status="NotInstalled"
  fi
  initDir "$1" "$2" "$3" "$4" "$5" "$status" "$7" "$8"
  zipDir "$1" "$3" "$4" "$status"
}


initPG () {
  if [ "$pgM" == "11" ]; then
    pgV=$P11
  elif [ "$pgM" == "12" ]; then
    pgV=$P12
  elif [ "$pgM" == "13" ]; then
    pgV=$P13
  elif [ "$pgM" == "14" ]; then
    pgV=$P14
  elif [ "$pgM" == "15" ]; then
    pgV=$P15
  elif [ "$pgM" == "16" ]; then
    pgV=$P16
  else
    echo "ERROR: Invalid PG version '$pgM'"
    exit 1
  fi

  if [ "$outDir" == "a64" ]; then
    outPlat="arm"
    if [ "$isEL9" == "True" ]; then
      outPlat="arm9"
    fi
  elif [ "$outDir" == "m64" ]; then
    outPlat="osx"
  else
    if [ "$isEL8" == "True" ]; then
      outPlat="el8"
    elif [ "$isEL9" == "True" ]; then
      outPlat="el9"
    else
      outPlat="amd"
    fi
  fi

  pgComp="pg$pgM"
  initDir "$pgComp" "pg" "$pgV" "$outPlat" "postgres/$pgComp" "Enabled" "5432" "nil"
  supplementalPG "$pgComp"
  zipDir "$pgComp" "$pgV" "$outPlat" "Enabled"

  writeSettRow "GLOBAL" "STAGE" "prod"
  writeSettRow "GLOBAL" "AUTOSTART" "off"

  if [ "$outPlat" == "osx" ]; then
    return
  fi

  if [ "$pgM" == "16" ] && [ "$isEL9" == "True" ]; then
    initC  "spock31-pg$pgM" "spock31"   "$spock31V"   "$outPlat" "postgres/spock31" "" "" "nil"
    initC  "hypopg-pg$pgM"  "hypopg"    "$hypoV"      "$outPlat" "postgres/hypopg"  "" "" "nil"
    initC  "pljava-pg$pgM"  "pljava"    "$pljavaV"    "$outPlat" "postgres/pljava"  "" "" "nil"
  fi

  if [ "$pgM" == "15" ] && [ "$isEL" == "True" ]; then

    if [ "$isEL9" == "True" ]; then
      initC  "spock31-pg$pgM" "spock31"   "$spock31V"        "$outPlat" "postgres/spock31"     "" "" "nil"
      initC "postgrest" "postgrest" "$postgrestV"  "$outPlat"  "postgres/postgrest"  "" "" "nil"
      initC  "pgcat2"  "pgcat2"  "$catV"  "$outPlat" "postgres/pgcat2" "" "" "nil"
      initC "hypopg-pg$pgM"  "hypopg"    "$hypoV"      "$outPlat" "postgres/hypopg"  "" "" "nil"
      initC "pljava-pg$pgM"  "pljava"  "$pljavaV"  "$outPlat" "postgres/pljava"  "" "" "nil"
      initC "timescaledb-pg$pgM" "timescaledb" "$timescaleV" "$outPlat" "postgres/timescale" "" "" "nil"
      initC "citus-pg$pgM" "citus" "$citusV" "$outPlat" "postgres/citus" "" "" "nil"
      initC "postgis-pg$pgM" "postgis" "$postgisV" "$outPlat" "postgres/postgis" "" "" "nil"
      initC "pglogical-pg$pgM" "pglogical" "$logicalV" "$outPlat" "postgres/logical" "" "" "nil"
      initC "anon-pg$pgM" "anon" "$anonV" "$outPlat" "postgres/anon" "" "" "nil"
      initC "plprofiler-pg$pgM" "plprofiler" "$profV" "$outPlat" "postgres/profiler" "" "" "nil"
      initC "pldebugger-pg$pgM" "pldebugger" "$debuggerV" "$outPlat" "postgres/pldebugger" "" "" "nil"
      initC "partman-pg$pgM" "partman" "$partmanV" "$outPlat" "postgres/partman" "" "" "nil"
      initC "orafce-pg$pgM" "orafce" "$orafceV" "$outPlat" "postgres/orafce" "" "" "nil"
      initC "audit-pg$pgM" "audit" "$audit15V" "$outPlat" "postgres/audit" "" "" "nil"
      initC "curl-pg$pgM"  "curl"    "$curlV"       "$outPlat" "postgres/curl"   "" "" "nil"
      initC "cron-pg$pgM" "cron" "$cronV" "$outPlat" "postgres/cron" "" "" "nil"
      initC "readonly-pg$pgM" "readonly" "$readonlyV" "$outPlat" "postgres/readonly" "" "" "nil"
      initC "hintplan-pg$pgM" "hintplan" "$hintV" "$outPlat" "postgres/hintplan" "" "" "nil"
    fi

  fi

  if [  "$isEL9" == "True" ]; then
    initC  "ncd"          "ncd"       "$ncdV"        ""         "nodectl-mqtt"       "" "" "nil"
    initC  "pgedge"       "pgedge"    "$pgedgeV"     ""         "postgres/pgedge"    "" "" "Y"
    initC  "backrest" "backrest" "$backrestV" "$outPlat" "postgres/backrest" "" "" "nil"
    #initC  "csvdiff" "csvdiff" "$csvdiffV" "$outPlat" "csvdiff" "" "" "nil"
    initC  "patroni"   "patroni"   "$patroniV" "" "postgres/patroni" "" "" "nil"
  fi
  ##initC "prompgexp"  "prompgexp"  "$prompgexpV"  ""  "prometheus/pg_exporter"  "" "" "Y"
  
  ##initC "instantclient" "instantclient" "$inclV" "" "oracle/instantclient" "" "" "Y"
  ##initC "kafka"     "kafka"     "$kfkV"   "" "kafka"            "" "" "Y"
  ##initC "apicurio"  "apicurio"  "$apicV"  "" "apicurio"         "" "" "nil"
  ##initC "debezium"  "debezium"  "$dbzV"   "" "debezium"         "" "" "Y"
  ##initC "pgadmin"   "pgadmin"   "$adminV" "" "postgres/pgadmin" "" "" "Y"

  ##initC "ora2pg"    "ora2pg"    "$ora2pgV" "" "postgres/ora2pg" "" "" "Y"

  return

}


setupOutdir () {
  rm -rf out
  mkdir out
  cd out
  mkdir $outDir
  cd $outDir
  out="$PWD"
  mkdir conf
  mkdir conf/cache
  conf="$SRC/conf"

  cp $conf/db_local.db  conf/.
  cp $conf/versions.sql  conf/.
  sqlite3 conf/db_local.db < conf/versions.sql
}


###############################    MAINLINE   #########################################
osName=`uname`
verSQL="versions.sql"

PLATFORM=`cat /etc/os-release | grep PLATFORM_ID | cut -d: -f2 | tr -d '\"'`
if [ "$PLATFORM" == "el8" ]; then
  isEL="True"
  isEL8="True"
  isEL9="False"
elif [ "$PLATFORM" == "el9" ] || [ "$PLATFORM" == "al2023" ]; then
  isEL="True"
  isEL8="False"
  isEL9="True"
else
  isEL8="False"
  isEL9="False"
  isEL="False"
fi

## process command line paramaters #######
while getopts "c:X:N:Ep:Rh" opt
do
    case "$opt" in
      X)  if [ "$OPTARG" == "l64" ] || [ "$OPTARG" == "posix" ] ||
	     [ "$OPTARG" == "a64" ] || [ "$OPTARG" == "m64" ]; then
            outDir="$OPTARG"
            setupOutdir
            OS_TYPE="POSIX"

            cp $CLI/cli.sh ./$api
            ln -s $api nc

            if [ "$outDir" == "posix" ]; then
              OS="???"
              platx="posix"
              plat="posix"
            elif [ "$outDir" == "posix" ]; then
              OS="OSX"
              platx=osx64
            else
              OS="LINUX"
              platx=$plat
            fi
          else
            fatalError "Invalid Platform (-X) option" "u"
          fi
          writeSettRow "GLOBAL" "PLATFORM" "$plat"
          if [ "$plat" == "posix" ]; then
            checkCmd "cp $CLI/install.py $OUT/."
          fi;;

      R)  writeSettRow "GLOBAL" "REPO" "$repo" "-v";;

      c)  zipOut="$OPTARG";;

      N)  NUM="$OPTARG";;

      E)  isENABLED=true;;

      p)  pgM="$OPTARG"
          checkCmd "initPG";;

      h)  printUsageMessage
          exit 1;;
    esac
done

if [ $# -lt 1 ]; then
  printUsageMessage
  exit 1
fi

finalizeOutput

exit 0
