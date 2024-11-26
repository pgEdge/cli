#!/bin/bash
cd "$(dirname "$0")"

pgSrc=$SOURCE/postgresql
binBld=/opt/pgbin-build/builds
source ./versions.sh

SPOCK_REPO=spock-private
SPOCK_BRANCH=main


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
  dir=$PWD/$SPOCK_REPO
  if [ ! -d "$dir" ]; then
    echo "missing $SPOCK_REPO"
    git clone https://github.com/pgedge/$SPOCK_REPO
  fi
  cd $dir

  git checkout $SPOCK_BRANCH
  git pull

  dp=$dir/patches
  export_patch DIFF1 "$dp" "$1"
  export_patch DIFF2 "$dp" "$2"
  export_patch DIFF3 "$dp" "$3"
  export_patch DIFF4 "$dp" "$4"
  export_patch DIFF5 "$dp" "$5"
  export_patch DIFF6 "$dp" "$6"

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

  p1=pg14-010-allow_logical_decoding_on_standbys.diff
  p2=pg14-015-attoptions.diff
  p3=pg14-020-LOG-to-DEBUG1.diff
  p4=pg14-025-logical_commit_clock.diff
  p5=pg14-030-per-subtrans-commit-ts.diff

elif [ "$majorV" == "15" ]; then
  pgV=$pg15V
  pgBuildV=$pg15BuildV

  p1=pg15-010-allow_logical_decoding_on_standbys.diff
  p2=pg15-015-attoptions.diff
  p3=pg15-020-LOG-to-DEBUG1.diff
  p4=pg15-025-logical_commit_clock.diff
  p5=pg15-030-per-subtrans-commit-ts.diff

elif [ "$majorV" == "16" ]; then
  pgV=$pg16V
  pgBuildV=$pg16BuildV

  p1=pg16-015-attoptions.diff
  p2=pg16-020-LOG-to-DEBUG1.diff
  p3=pg16-025-logical_commit_clock.diff
  p4=pg16-030-per-subtrans-commit-ts.diff

elif [ "$majorV" == "17" ]; then
  pgV=$pg17V
  pgBuildV=$pg17BuildV

  p1=pg17-015-attoptions.diff
  p2=pg17-020-LOG-to-DEBUG1.diff
  p3=pg17-025-logical_commit_clock.diff
  p4=pg17-030-per-subtrans-commit-ts.diff
  p5=pg17-090-init_template_fix.diff

fi

export_patches $p1 $p2 $p3 $p4 $p5
runPgBin "$binBld" "$pgSrc-$pgV.tar.gz" "$pgBuildV"

exit 0
