#!/bin/bash
cd "$(dirname "$0")"

pgSrc=$SOURCE/postgresql
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
    echo "majorV = $majorV"
    cmd="./build-pgbin.sh -a $pOutDir -t $pPgSrc -n $pBldV"
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

function export_patches {
  dir=$PWD/spock-private
  cd $dir

  git checkout main
  git pull

  dp=$dir/patches
  export_patch DIFF1 "$dp" "$1"
  export_patch DIFF2 "$dp" "$2"
  export_patch DIFF3 "$dp" "$3"

  cd ..
}


function export_patch {
  DIFF="$1"
  dirp="$2"
  patch="$3"

  if [ "x$patch" == "x" ]; then
    return
  fi

  p="$dirp/$patch"
  if [ -f "$p" ]; then
    export $DIFF="$p"
  else
    echo "FATAL ERROR: Missing $DIFF $p"
    exit 1
  fi

}

########################################################################
##                     MAINLINE                                       ##
########################################################################

## validate input parm
majorV="$1"
optional="$2"

if [ "$majorV" == "12" ]; then
  pgV=$pg12V
  pgBuildV=$pg12BuildV

elif [ "$majorV" == "13" ]; then
  pgV=$pg13V
  pgBuildV=$pg13BuildV

elif [ "$majorV" == "14" ]; then
  pgV=$pg14V
  pgBuildV=$pg14BuildV

  p1=pg14-005-log_old_value.diff
  p2=pg14-010-allow_logical_decoding_on_standbys.diff
  p3=pg14-012-hidden_columns.diff
  export_patches "$p1" "$p2" "$p3"

elif [ "$majorV" == "15" ]; then
  pgV=$pg15V
  pgBuildV=$pg15BuildV

  p1=pg15-005-log_old_value.diff
  p2=pg15-010-allow_logical_decoding_on_standbys.patch
  p3=pg15-012-hidden_columns.diff
  export_patches "$p1" "$p2" "$p3"

elif [ "$majorV" == "16" ]; then
  pgV=$pg16V
  pgBuildV=$pg16BuildV

  p1=pg16-005-log_old_value.diff
  p2=pg16-012-hidden_columns.diff
  export_patches "$p1" "$p2"

elif [ "$majorV" == "17" ]; then
  pgV=$pg17V
  pgBuildV=$pg17BuildV

  p1=pg17-005-log_old_value.diff
  p2=pg17-012-hidden_columns-v3.diff
  export_patches "$p1" "$p2"

fi

runPgBin "$binBld" "$pgSrc-$pgV.tar.gz" "$pgBuildV"

exit 0
