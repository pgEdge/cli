
set -x

pgedge/pgedge stop
bakup-pgedge/pgedge stop
sleep 2

rm -rf pgedge

cp -r bakup-pgedge pgedge
sleep 2

pgedge/pgedge start
cp $CLI/upgrade-cli.py pgedge/.
