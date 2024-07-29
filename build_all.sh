#!/bin/bash
cd "$(dirname "$0")"

source ./env.sh
rc=$?
if [ ! "$rc" == "0" ]; then
  fatalError "YIKES - no env.sh found"
fi

num_p=$#
if [ ! $num_p == "0" ] && [ ! $num_p == "1"  ] && [ ! $num_p == "2" ]; then
  fatalError "must be zero, one, or two parms"
fi

if [ "$1" == "" ]; then
  majorV=16
  echo ""
  echo "### Defaulting to pg $majorV ###"
else
  majorV=$1
fi

if [ "$majorV" == "12" ]; then
  minorV=$P12
elif [ "$majorV" == "13" ]; then
  minorV=$P13
elif [ "$majorV" == "14" ]; then
  minorV=$P14
elif [ "$majorV" == "15" ]; then
  minorV=$P15
elif [ "$majorV" == "16" ]; then
  minorV=$P16
elif [ "$majorV" == "17" ]; then
  minorV=$P17
else
  echo "ERROR: pg must be 12-17"
  exit 1
fi

if [ "$OUT" == "" ]; then
  echo "ERROR: Environment is not set..."
  exit 1
fi


buildPkgBundle() {
  bundle_nm="$1"
  majorV="$2"

  pgV=`echo $3 | tr - .`
  spockV=`echo $4 | tr - .`
  cliV="$5"

  echo "## buildPkgBundle() $bundle_nm ##"
  ##echo "# 1. bundle_nm = $bundle_nm"
  ##echo "# 2.    majorV = $majorV"
  ##echo "# 3.       pgV = $pgV"
  ##echo "# 4.    spockV = $spockV"
  ##echo "# 5.      hubV = $hubV"
  ##echo "#"

  source bp.sh
  echo ""
  sleep 2
  echoCmd "./pgedge setup --pg_ver $majorV --extensions core"

  ## Cleanup cruft #####################
  cd ../..
  base_d=out/posix
  rm -r $base_d/ctlibs
  data_d=$base_d/data
  rm -f $data_d/logs/*
  rm -f $data_d/conf/*.pid
  rm $data_d/conf/cache/*

  rm -rf /tmp/$bundle_nm
  mv $base_d /tmp/$bundle_nm

  echo ""
  echoCmd "src/packages/run_fpm.sh  $bundle_nm  $majorV  $pgV  $spockV  $hubV"
}


buildALL () {
  bigV=$1
  fullV=$2
  echo ""
  echo "################## BUILD_ALL $bigV $fullV ###################"

  buildONE $outDir $bigV $fullV 
  
}


buildONE () {
  vPlat=$1
  vBig=$2
  vFull=$3

  if [ "$4" == "false" ]; then
    return
  fi
  parms="-X $vPlat -c $bundle -N $vFull -p $vBig"
  echo ""
  echo "### BUILD_ONE $parms ###"
  ./build.sh $parms
  rc=`echo $?`
  if [ $rc -ne 0 ]; then
    exit $rc
  fi
}


############# MAINLINE ######################

outp="out/posix"

if [ -d $outp ]; then
  echo "Removing current '$outp' directory..."
  $outp/$api stop
  sleep 2
  $sudo rm -rf $outp
fi

if [ ! "$2" == "" ]; then
  if [ ! "$2" == "rpm" ] && [ ! "$2" == "deb" ]; then
     fatalError "ERROR:  2nd parm is pkg_type (only 'rpm' & 'deb' are supported)"
  fi

  vers=$(echo $hubV | tr "." "\n")
  let x=0
  for v in $vers
  do
    let x=x+1
    if [ "$x" == "1" ]; then
      newV=$v
    elif [ "$x" == "2" ]; then
      vv=`printf '%02d\n' "$v"`
      newV=$newV.$vv
    elif [ "$x" == "3" ]; then
      newV=$newV-$v
    fi
  done

  pf="arm64"
  if [ `arch` == "x86_64" ]; then
    pf="amd64"
  fi
  bundle_nm=pgedge-$newV-pg-$minorV-$pf

  buildPkgBundle "$bundle_nm" "$majorV" "$minorV" "$spock40V" "$hubV" 
  rc=$?

  exit $rc
fi


echo ""
echo "############### Build Package Manager ###################"
rm -f $OUT/hub-$hubV*
rm -f $OUT/$bundle-cli-$hubV*
./build.sh -X posix -c $bundle-cli -N $hubV

buildALL $majorV $minorV

echo ""
exit 0
