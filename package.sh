#!/bin/bash
cd "$(dirname "$0")"
source env.sh

PKG_TYPE=rpm

makeBundle () {
  pgv="$1"
  plat="$2"
  bundle_nm="$3"

  cmd="./build_all.sh $pgv $plat $bundl_nm"
}


############## MAINLINE #############################################

# echo "#    hubV = $hubV"
# echo "# outPlat = $outPlat"

if [ "$OUT" == "" ]; then
  fatalError "\$OUT environment is not set"
fi

PKGR=src/packages/make_package.sh
if [ ! -f $PKGR ]; then
  fatalError "Cannot locate file \"$PKGR\""
fi

if [ $# -ne 1 ]; then
  fatalError "pg_ver variable is required (such as '16')"
fi

setPGV "$1"
# echo "#   pgV = $pgV"
# echo "# pgMAJ = $pgMAJ"
# echo "# pgMIN = $pgMIN"
# echo "# pgREV = $pgREV"

vers="--major_ver $pgMAJ --minor_ver $pgMIN --release $pgREV"
# echo "#    vers = $vers"
bundle=bundle-pg$pgMAJ.$pgMIN.$pgREV-edge$hubV-$outPlat
# echo "# bundle = $bundle"

cmd="$PKGR $vers --bundle_name $bundle"

echoCmd "$cmd"

exit 1

cd $OUT

rm -rf pgedge

