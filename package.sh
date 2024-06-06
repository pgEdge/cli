#!/bin/bash
cd "$(dirname "$0")"

source env.sh
# echo "#    hubV = $hubV"
# echo "# outPlat = $outPlat"

if [ "$OUT" == "" ]; then
  fatalError "environment is not set"
fi

pkgr=src/packages/make_package.sh
if [ ! -f $pkgr ]; then
  fatalError "Cannot locate file ($pkgr)"
fi

if [ $# -ne 1 ]; then
  fatalError "only the pgParm variable is allowed such as '16'"
fi

setPGV "$1"
# echo "#   pgV = $pgV"
# echo "# pgMAJ = $pgMAJ"
# echo "# pgMIN = $pgMIN"
# echo "# pgREV = $pgREV"

vers="--major_version $pgMAJ --minor_version $pgMIN --release $pgREV"
echo "#    vers = $vers"
bndl=bndl-$pgMAJ.$pgMIN.$pgREV-$hubV-$outPlat
echo "# $bndl = $bndl"

cmd="$pkgr $vers --rpm_release $pgREV"

echoCmd "$cmd"

exit 1

cd $OUT

rm -rf pgedge

