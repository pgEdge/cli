#!/bin/bash

source ./env.sh
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "YIKES - no env.sh found"
  exit 1
fi;

majorV="$1"
if [ "$majorV" == "12" ]; then
  minorV=$P12
elif [ "$majorV" == "13" ]; then
  minorV=$P13
elif [ "$majorV" == "14" ]; then
  minorV=$P14
elif [ "$majorV" == "15" ]; then
  minorV=$P15
elif [ "$majorV" == "i14" ]; then
  minorV=$I14
elif [ "$majorV" == "all" ]; then
  minorV=all
else
  echo "ERROR: pg must be 12-15, or all"
  exit 1
fi

if [ ! "$2" == "" ]; then
  outDir="$2"
fi

if [ "$OUT" == "" ]; then
  echo "ERROR: Environment is not set..."
  exit 1
fi


buildALL () {
  bigV=$1
  fullV=$2
  echo ""
  echo "################## BUILD_ALL $bigV $fullV ###################"

  if [ "$bigV" == "all" ]; then
    buildONE $outDir "12" $P12
    buildONE $outDir "13" $P13
    buildONE $outDir "14" $P14
    buildONE $outDir "15" $P15
  else
    buildONE $outDir $bigV $fullV 
  fi
  
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


echo "############### Build Package Manager ###################"
rm -f $OUT/hub-$hubV*
rm -f $OUT/$bundle-$api-$hubV*
./build.sh -X posix -c $bundle-$api -N $hubV

buildALL $majorV $minorV

echo ""
exit 0
