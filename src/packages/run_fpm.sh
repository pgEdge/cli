#!/bin/bash
cd "$(dirname "$0")"

bundle="$1"
major_v="$2"

##suffix=arm
##if [ `arch` == "x86_64" ]; then
##   suffix="amd"
##fi

pkg_type=deb
yum --version > /dev/null 2>&1
rc=$?
if [ $rc" == "0" ]; then
  pkg_type=rpm
fi
pkg_file=$bundle.$pkg_type


echo ""
##echo "####### src/packages/run_fpm.sh ################"
##echo "# 1.  bundle = $bundle"
##echo "# 2. major_v = $major_v"
##echo "# 3.    pg_v = $pg_v"
##echo "# 4. spock_v = $spock_v"
##echo "# 5.   cli_v = $cli_v"
##echo "#"
echo "#   pkg_file = $pkg_file"
##echo "###############################################"
##echo ""

fpm --version > /dev/null 2>&1
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: fpm not installed (rc=$rc)"
  exit 1
fi

dir_bundle=/tmp/$bundle
if [ ! -d /tmp/$bundle ]; then
  echo "ERROR: missing bundle directory $dir_bundle"
  exit 1
fi

ctl=$dir_bundle/pgedge

cmd="$ctl set GLOBAL REPO https://pgedge-upstream.s3.amazonaws.com/REPO"
echo $cmd; $cmd

cmd="$ctl set GLOBAL PG_VER $major_v"
echo $cmd; $cmd

$ctl info
sleep 2

echo "#"
echo "# running FPM... (be patient for about 60 seconds)"

rm -f $rpm_file

set -x

if [ "$pkg_type" == "rpm" ]; then
  opt="--no-rpm-autoreqprov --rpm-tag '%define _build_id_links none'"
  opt="$opt --rpm-tag '%undefine _missing_build_ids_terminate_build'"
  options="$opt --rpm-user pgedge"
else
  options="--deb-user pgedge"
fi

fpm \
  -s dir -t $pkg_type \
  -p $pkg_file \
  --name pgedge \
  --version $pg_v.$spock_v.$cli_v \
  --architecture `arch` \
  --description "pgedge bundle" \
  --url "https://pgedge.com" \
  --maintainer "support@pgedge.com" \
  --before-install ./before-install.sh \
  --after-install ./after-install.sh \
  --after-remove ./after-remove.sh \
  $options $dir_bundle/.=/opt/pgedge/.

rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: fpm failed (rc=$rc)"
  exit 1
fi

echo "#"
echo "# moving package to \$OUT"

rm -f $OUT/$rpm_file

mv $rpm_file $OUT/.

##cd $OUT
##ln -s $rpm_file $rpm_alias
##
##touch $rpm_file
##touch $rpm_alias

exit 0

