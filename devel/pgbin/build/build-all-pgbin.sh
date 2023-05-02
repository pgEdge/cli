#!/bin/bash
cd "$(dirname "$0")"

pgSrc=$SRC/postgresql
binBld=/opt/pgbin-build/builds
source ./versions.sh


function runPgBin {
  ##echo "#"
  pOutDir=$1
  ##echo "# outDir = $pOutDir"
  pPgSrc=$2
  ##echo "# pPgSrc = $pPgSrc"
  pBldV=$3
  ##echo "#   BldV = $pBldV"

  if [ "$IVORY" = "True" ]; then
    cmd="./build-pgbin.sh -a $pOutDir -t $pPgSrc -n $pBldV"
  else
    #bncrSrc=$SRC/bouncer-$bouncerFullV.tar.gz
    #odbcSrc=$SRC/psqlodbc-$odbcV.tar.gz
    #bkrstSrc=$SRC/backrest-$backrestFullV.tar.gz
    #pool2Src=$SRC/pool2-$pool2FullV.tar.gz
    #agentSrc=$SRC/agent-$agentV.tar.gz
    echo "majorV = $majorV"
    #if [[ "$majorV" > "13" ]]; then
    #  cmd="./build-pgbin.sh -a $pOutDir -t $pPgSrc -n $pBldV -b $bncrSrc -p $pool2Src"
    #else
      cmd="./build-pgbin.sh -a $pOutDir -t $pPgSrc -n $pBldV"
    #fi
  fi

  cmd="$cmd $optional"
  echo "$cmd"
  $cmd
  if [[ $? -ne 0 ]]; then
    echo "Build Failed"
    exit 1	
  fi

  return
}

########################################################################
##                     MAINLINE                                       ##
########################################################################

## validate input parm
majorV="$1"
optional="$2"

if [ "$majorV" == "11" ]; then
  pgV=$pg11V
  pgBuildV=$pg11BuildV
elif [ "$majorV" == "12" ]; then
  pgV=$pg12V
  pgBuildV=$pg12BuildV
elif [ "$majorV" == "13" ]; then
  pgV=$pg13V
  pgBuildV=$pg13BuildV
elif [ "$majorV" == "14" ]; then
  pgV=$pg14V
  pgBuildV=$pg14BuildV

elif [ "$majorV" == "15" ]; then
  pgV=$pg15V
  pgBuildV=$pg15BuildV

  cd spock
  git checkout REL3_0_STABLE
  git pull
  diff1=$PWD/pg15-log_old_value.diff
  if [ -f "$diff1" ]; then
    export DIFF1="$diff1"
  else
    echo "FATAL ERROR: Missing $diff1"
    exit 1
  fi
  cd ..

elif [ "$majorV" == "16" ]; then
  pgV=$pg16V
  pgBuildV=$pg16BuildV

  cd spock
  git checkout pg_16_compatibility
  git pull
  diff1=$PWD/pg16-log_old_value.diff
  if [ -f "$diff1" ]; then
    export DIFF1="$diff1"
  else
    echo "FATAL ERROR: Missing $diff1"
    exit 1
  fi
  cd ..
fi

runPgBin "$binBld" "$pgSrc-$pgV.tar.gz" "$pgBuildV"

exit 0
