#!/bin/bash
cd "$(dirname "$0")"

bundle="$1"
major_v="$2"
pg_v="$3"
spock_v="$4"
cli_v="$5"

suffix=el9-`arch`
rpm_file=pgedge-$pg_v-$spock_v-$cli_v-$suffix.rpm
rpm_alias=pgedge-$major_v-$suffix.rpm

echo ""
echo "####### src/packages/run_fpm.sh ################"
echo "# 1.  bundle = $bundle"
echo "# 2. major_v = $major_v"
echo "# 3.    pg_v = $pg_v"
echo "# 4. spock_v = $spock_v"
echo "# 5.   cli_v = $cli_v"
echo "#"
echo "#   rpm_file = $rpm_file"
echo "#  rpm_alias = $rpm_alias"
echo "############################"
echo ""

fpm --version > /dev/null 2>&1
rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: fpm not installed (rc=$rc)"
  exit 1
fi

if [ ! "$#" == "5" ]; then
  echo "ERROR: requires 5 parms: {bundle} {major_v} {pg_v} {spock_v} {cli_v}"
  exit 1
fi

dir_bundle=/tmp/$bundle
if [ ! -d /tmp/$bundle ]; then
  echo "ERROR: missing bundle directory $dir_bundle"
  exit 1
fi

rm -f $rpm_file

echo "#"
echo "# running FPM ... (be patient)"

fpm \
  -s dir -t rpm \
  -p $rpm_file \
  --name pgedge \
  --version $pg_v.$spock_v.$cli_v \
  --architecture `arch` \
  --description "pgedge bundle" \
  --url "https://pgedge.com" \
  --maintainer "support@pgedge.com" \
  --before-install ./before-install.sh \
  --after-install ./after-install.sh \
  --no-rpm-autoreqprov \
  --rpm-tag '%define _build_id_links none' \
  --rpm-tag '%undefine _missing_build_ids_terminate_build' \
  --rpm-user pgedge \
  $dir_bundle/.=/opt/pgedge/.

rc=$?
if [ ! "$rc" == "0" ]; then
  echo "ERROR: fpm failed (rc=$rc)"
  exit 1
fi

echo "#"
echo "# moving package & alias to \$OUT"
rm -f $OUT/$rpm_file
rm -f $OUT/$rpm_alias

set -x

mv $rpm_file $OUT/.
cd $OUT
ln -s $rpm_file $rpm_alias

exit 0

