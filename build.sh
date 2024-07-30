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
  echo "#                Copyright (c) 2022-2024 PGEDGE                     #"
  echo "#-------------------------------------------------------------------#"
  echo "# -p $P17 $P16 $P15 $P14 $P13 $P12"
  echo "# -b hub-$hubV"
  echo "#-------------------------------------------------------------------#"
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
  dbLocal="$out/data/conf/db_local.db"
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

  dbLocal="$out/data/conf/db_local.db"
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

  ## echo "DEBUG initDir(1=$1, 2=$2, 3=$3 4=$4, 5=$5, 6=$6, 7=$7, 8=$8"

  if [ "$pStatus" == "" ]; then
    pStatus="NotInstalled"
  fi

  if [ "$pStatus" == "NotInstalled" ] && [ "$isENABLED" == "true" ]; then
    pStatus="Enabled"
  fi

  if [ "$pStatus" == "NotInstalled" ] && [ ! "$zipOut" == "off" ]; then
     if [ "$pExt" == "" ]; then
       fileNm=$OUT/$pComponent-$pPreNum.tgz
     else
       fileNm=$OUT/$pComponent-$pPreNum-$pExt.tgz
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
  myOrigFile=$myOrigDir.tgz

  if [ "$pStageSubDir" == "nil" ]; then
    thisDir=$IN
  else
    thisDir=$IN/$pStageSubDir
  fi

  if [ ! -d "$thisDir/$myOrigDir" ]; then
    origFile=$thisDir/$myOrigFile
    if [ -f $origFile ]; then
      checkCmd "tar -xf $origFile"      
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

  if [ -f $myNewDir/LICENSE.TXT ]; then
    mv $myNewDir/LICENSE.TXT $myNewDir/$pComponent-LICENSE.TXT
  fi

  if [ -f $myNewDir/src.tar.gz ]; then
    mv $myNewDir/src.tar.gz $myNewDir/$pComponent-src.tar.gz
  fi

  rm -f $myNewDir/logs/*

  rm -rf $myNewDir/manual

  rm -rf $myNewdir/build*
  rm -rf $myNewDir/.git*
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
  myTarball=$baseName.tgz
  myChecksum=$myTarball.sha512

  if [ ! -f "$OUT/$myTarball" ] && [ ! -f "$OUT/$myChecksum" ]; then
    echo "COMPONENT = '$baseName' '$pStatus'"
    options=""
    if [ "$osName" == "Linux" ]; then
      options="--owner=0 --group=0"
    fi
    checkCmd "tar $options -czf $myTarball $pComponent"
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
  checkCmd "mkdir -p hub/scripts"

  checkCmd "cp $CLI/*.py        hub/scripts/."
  checkCmd "cp $CLI/*.sh        hub/scripts/."
  checkCmd "cp -r $CLI/fire     hub/scripts/."
  checkCmd "cp -r $CLI/contrib  hub/scripts/."
  checkCmd "cp -r $CLI/lib      hub/scripts/."
  checkCmd "cp -r $CLI/ini      hub/scripts/."
  checkCmd "cp -r $CLI/sql      hub/scripts/."
  checkCmd "cp -r $CLI/sh       hub/scripts/."

  checkCmd "mkdir -p hub/doc"
  checkCmd "cp $CLI/../README.md  hub/doc/."
  zipDir "hub" "$hubV" "" "Enabled"

  checkCmd "cp data/conf/versions.sql  ."
  writeFileChecksum "versions.sql"

  checkCmd "cd $HUB"

  if [ ! "$zipOut" == "off" ] &&  [ ! "$zipOut" == "" ]; then
    zipExtension="tgz"
    options=""
    if [ "$osName" == "Linux" ]; then
      options="--owner=0 --group=0"
    fi
    zipCommand="tar $options -czf"
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
  setPGV "$pgM"

  writeSettRow "GLOBAL" "STAGE" "prod"
  writeSettRow "GLOBAL" "AUTOSTART" "off"

  initC "ctlibs"  "ctlibs"  "$ctlibsV"  "" "ctlibs"         "" "" "Y"

  pgComp="pg$pgM"
  initDir "$pgComp" "pg" "$pgV" "$outPlat" "postgres/$pgComp" "Enabled" "5432" "nil"
  supplementalPG "$pgComp"
  zipDir "$pgComp" "$pgV" "$outPlat" "Enabled"

  if [ "$pgM" \> "13" ] && [ "$pgM" \< "18" ]; then
    initC "lolor-pg$pgM"      "lolor"      "$lolorV"     "$outPlat" "postgres/lolor"     "" "" "nil"
    initC "snowflake-pg$pgM"  "snowflake"  "$snwflkV"    "$outPlat" "postgres/snowflake" "" "" "nil"
  fi

  if [ "$pgM" \> "13" ] && [ "$pgM" \< "17" ]; then
    initC "spock33-pg$pgM"    "spock33"    "$spock33V"   "$outPlat" "postgres/spock33"   "" "" "nil"
  fi

  if [ "$pgM" \> "13" ] && [ "$pgM" \< "18" ]; then
    initC "spock40-pg$pgM"    "spock40"    "$spock40V"   "$outPlat" "postgres/spock40"   "" "" "nil"
  fi

  if [ "$pgM" == "14" ] || [ "$pgM" == "15" ]; then
    initC "foslots-pg$pgM"    "foslots"    "$foslotsV"   "$outPlat" "postgres/foslots"    "" "" "nil"
  fi

  if [ "$isEL" == "True" ]; then
    initC "backrest"     "backrest"     "$backrestV" "$outPlat" "postgres/backrest" "" "" "nil"
    initC "etcd"         "etcd"         "$etcdV"     "$outPlat" "etcd"              "" "" "nil"
    initC "pgcat"        "pgcat"        "$catV"      "$outPlat" "postgres/pgcat"    "" "" "nil"
    initC "patroni"      "patroni"      "$patroniV"  ""         "patroni"           "" "" "nil"
    initC "firewalld"    "firewalld"    "$firwldV"   ""         "firewalld"         "" "" "nil"
  fi

  if [ "$pgM" == "16" ]; then
    initC "audit-pg$pgM"      "audit"      "$audit16V"   "$outPlat" "postgres/audit"     "" "" "nil"
    initC "hintplan-pg$pgM"   "hintplan"   "$hint16V"    "$outPlat" "postgres/hintplan"  "" "" "nil"
  fi

  if [ "$pgM" == "15" ]; then
    initC "audit-pg$pgM"      "audit"      "$audit15V"   "$outPlat" "postgres/audit"     "" "" "nil"
    initC "hintplan-pg$pgM"   "hintplan"   "$hint15V"    "$outPlat" "postgres/hintplan"  "" "" "nil"
  fi

  if [ "$pgM" == "15" ] || [ "$pgM" == "16" ]; then
    initC "plv8-pg$pgM"       "plv8"       "$v8V"        "$outPlat" "postgres/plv8"       "" "" "nil"
    initC "wal2json-pg$pgM"   "wal2json"   "$wal2jV"     "$outPlat" "postgres/wal2json"   "" "" "nil"
    initC "pldebugger-pg$pgM" "pldebugger" "$debuggerV"  "$outPlat" "postgres/pldebugger" "" "" "nil"
    initC "hypopg-pg$pgM"     "hypopg"     "$hypoV"      "$outPlat" "postgres/hypopg"     "" "" "nil"
    ##initC "curl-pg$pgM"       "curl"       "$curlV"      "$outPlat" "postgres/curl"       "" "" "nil"
    initC "orafce-pg$pgM"     "orafce"     "$orafceV"    "$outPlat" "postgres/orafce"     "" "" "nil"
    initC "vector-pg$pgM"     "vector"     "$vectorV"    "$outPlat" "postgres/vector"     "" "" "nil"
    initC "plprofiler-pg$pgM" "plprofiler" "$profV"      "$outPlat" "postgres/profiler"   "" "" "nil"
    initC "postgis-pg$pgM"    "postgis"    "$postgisV"   "$outPlat" "postgres/postgis"    "" "" "nil"
    initC "cron-pg$pgM"       "cron"       "$cronV"      "$outPlat" "postgres/cron"       "" "" "nil"
    initC "partman-pg$pgM"    "partman"    "$partmanV"   "$outPlat" "postgres/partman"    "" "" "nil"

    initC "citus-pg$pgM"       "citus"       "$citusV"       "$outPlat" "postgres/citus"       "" "" "nil"
    initC "timescaledb-pg$pgM" "timescaledb" "$timescaleV"   "$outPlat" "postgres/timescale"   "" "" "nil"
    initC "setuser-pg$pgM"     "setuser"     "$setuserV"     "$outPlat" "postgres/setuser"     "" "" "nil"
    initC "permissions-pg$pgM" "permissions" "$permissionsV" "$outPlat" "postgres/permissions" "" "" "nil"

    ##initC "pljava-pg$pgM"     "pljava"     "$pljavaV"    "$outPlat" "postgres/pljava"     "" "" "nil"
    ##if [ `arch` != "aarch64" ]; then
    ##  initC "oraclefdw-pg$pgM"  "oraclefdw"  "$oraclefdwV" "$outPlat" "postgres/oraclefdw" "" "" "nil"
    ##fi
  fi

  initC "prompgexp"    "prompgexp"    "$prompgexpV" "$outPlat" "postgres/prompgexp" "" "" "nil"

  ## initC "postgrest"    "postgrest"    "$postgrestV" "$outPlat" "postgres/postgrest" "" "" "nil"
  ## initC "prest"        "prest"        "$prestV"    "$outPlat" "pREST"             "" "" "nil"
  ## initC "pgadmin4"     "pgadmin4"     "$adminV"    ""         "postgres/pgadmin4" "" "" "Y"

  return
}


setupOutdir () {
  rm -rf out
  mkdir out
  cd out
  mkdir $outDir
  cd $outDir
  out="$PWD"

  mkdir -p data/logs
  d_conf=data/conf
  mkdir -p $d_conf/cache

  s_conf="$SRC/conf"
  cp $s_conf/db_local.db  $d_conf/.
  cp $s_conf/versions.sql  $d_conf/.
  sqlite3 $d_conf/db_local.db < $d_conf/versions.sql
}


##########################    MAINLINE   ####################################
osName=`uname`
verSQL="versions.sql"


## process command line paramaters #######
while getopts "c:X:N:Ep:Rh" opt
do
    case "$opt" in
      X)  if [ "$OPTARG" == "l64" ] || [ "$OPTARG" == "posix" ] ||
	     [ "$OPTARG" == "a64" ] || [ "$OPTARG" == "m64" ]; then
            outDir="$OPTARG"
            setupOutdir
            OS_TYPE="POSIX"


            cp $CLI/sh/cli.sh     ./pgedge

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
