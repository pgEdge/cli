#!/bin/bash
cd "$(dirname "$0")"

# Script to generate pgedge builds and the corresponding tgz bundles with mode-based customization.
# Supports '-m MODE' switch for 'stable' (default) or 'current' modes.
# In 'stable' mode, after generating builds, strips specified unstable components using 'removeComponentFromOut' from env.sh.
# In 'current' mode, includes all components.

TGZ_REPO="https://pgedge-download.s3.amazonaws.com/REPO"

source env.sh

set -ex

cmd () {
  echo "# $1"
  $1
  rc=$?
  if [ ! "$rc" == "0" ]; then
    echo "ERROR: rc=$rc  Stopping Script"
    exit $rc
  fi

}

show_help() {
  cat << EOF
Usage: $0 [OPTIONS]
  -m MODE         Build mode: 'stable' (default) or 'current'
  -h              Show help

Examples:
  $0
  $0 -m current
EOF
}

MODE="stable"
while getopts "m:h" opt; do
  case $opt in
    m) MODE="$OPTARG" ;;
    h) show_help; exit 0 ;;
    \?) show_help; exit 1 ;;
  esac
done
# check that the mode passed is either stable or current
if [[ "$MODE" != "stable" && "$MODE" != "current" ]]; then
  echo "[ERROR] Invalid mode: $MODE"
  show_help
  exit 1
fi

## MAINLINE ###################################

vers="15 16 17"
cmd "rm -f $OUT/*"
for ver in ${vers}; do
  echo ""
  cmd "./build_all.sh $ver"
done

sleep 5
# If mode is 'stable' and removeComponentFromOut has a value defined in env.sh,
# strip the corresponding unstable component packages (e.g., spock50) from the build.
# This ensures only stable components are included in the tgz bundle.
# In 'current' mode, this step is skipped, preserving all stable and unstable components
# Wildcards (*) in removeComponentFromOut are not supported.
removeComponentFromOut="$(echo -n "$removeComponentFromOut" | xargs)"
if [[ "$MODE" == "stable" && -n "$removeComponentFromOut" ]]; then
  if [[ "$removeComponentFromOut" == *"*"* ]]; then
    echo "[ERROR] removeComponentFromOut should not contain a wildcard (*). Skipping removal."
  else
    echo "[INFO] [STABLE MODE] Attempting to remove files matching: $OUT/${removeComponentFromOut}*.tgz"
    removed_files=$(rm -vf "$OUT/${removeComponentFromOut}"*.* 2>&1 | wc -l)
    echo "[INFO] Removed $removed_files files for $removeComponentFromOut."
  fi
fi

./bp.sh

# remove large ctlib tarballs of different architecture
if [ `arch` == "aarch64" ]; then
  rm -f $OUT/*ctlibs*amd.tgz
else
  rm -f $OUT/*ctlibs*arm.tgz
fi

bndl="pgedge-$hubVV-$OS.tgz"

cd /tmp

rm -f $bndl
rm -rf pgedge

cp $CLI/install.py /tmp/.
python3 install.py
cmd "pgedge/pgedge set GLOBAL REPO $TGZ_REPO"

cache=pgedge/data/conf/cache
cmd "cp -v  $PGE/src/repo/* $OUT/."
cmd "cp $OUT/* $cache/."

cmd "cp -r $DEVEL/packages $cache/."
cmd "python3 pgedge/hub/scripts/get_old.py"
cmd "cp $HIST/out_old/* $cache/."

echo "RUNNING pigz..."
tar --use-compress-program="pigz -8 --recursive" -cf $bndl pgedge

rm -f install.py
rm -rf pgedge

mv /tmp/$bndl $OUT/.
ls -lh /$OUT/$bndl

# Create the version file (used by CloudFront pgedge-latest-{arch}.tgz redirects) in $OUT
echo "$hubVV" > "$OUT/pgedge-latest-$OS.version"
echo "Created version file: $OUT/pgedge-latest-$OS.version"
