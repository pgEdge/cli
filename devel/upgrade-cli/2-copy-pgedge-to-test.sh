
set -x

if [ -f test-pgedge/pgedge ]; then
  test-pgedge/pgedge stop
fi

rm -rf test-pgedge

cp -r pgedge test-pgedge

cp $CLI/upgrade-cli.py test-pgedge/.

t_pge=test-pgedge/pgedge

$t_pge remove pg16 --rm-data > /dev/null 2>&1

## now we do a `setup` from cache
$t_pge setup $CONN

$t_pge info
$t_pge list


