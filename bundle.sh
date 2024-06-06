#!/bin/bash
cd "$(dirname "$0")"

source env.sh

if [ "$OUT" == "" ]; then
  echo "ERROR: Environment is not set"
  exit 1
fi




setPGV "$1"

echo "#     pgV = $pgV"
echo "#    hubV = $hubV"
echo "# outPlat = $outPlat"

exit 1

## pgedge-16.3.2-24.6.5-arm9

cd $OUT

rm -rf pgedge

