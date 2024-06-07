#!/bin/sh

source ../versions.sh

set -x

pgV=$pg16V
rls=$pg16BuildV
M=`echo "$pgV" | cut -d '.' -f 1`
m=`echo "$pgV" | cut -d '.' -f 2`

./make_package.sh --major_version $M --minor_version $m --release $rls --rpm_release $rls 
