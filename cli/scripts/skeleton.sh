

function test14 {
  pgV=pg14
  ./nodectl install pg14; 
  ./nodectl start pg14 -y -d demo;

  ./nodectl install audit-$pgV         -d demo
  ./nodectl install timescaledb-$pgV   -d demo
}


function test15 {
  pgV=pg15
  ./nodectl install pg15; 
  ./nodectl start pg15 -y -d demo;

  ./nodectl install plprofiler-$pgV
  ./nodectl install spock-$pgV         -d demo
  ./nodectl install pldebugger-$pgV    -d demo

  ./nodectl install repack-$pgV        -d demo
  ./nodectl install orafce-$pgV        -d demo
  ./nodectl install partman-$pgV       -d demo
  ./nodectl install cron-$pgV

  #./nodectl install bulkload-$pgV      -d demo

  #./nodectl install plv8-$pgV          -d demo

  if [ `arch` == "aarch64" ]; then
    ./nodectl install postgis-$pgV      -d demo
  #else
  #  ./nodectl install mysqlfdw-$pgV     -d demo
  #  ./nodectl install mongofdw-$pgV     -d demo
  #  ./nodectl install oraclefdw-$pgV    -d demo
  #  ./nodectl install esfdw-$pgV        -d demo

  ./nodectl install multicorn2-$pgV    -d demo
  ./nodectl install hintplan-$pgV      -d demo
  #./nodectl install citus-$pgV         -d demo

  fi

  #./nodectl install decoderbufs-$pgV   -d demo
  #./nodectl install hypopg-$pgV        -d demo
}


cd ../..

if [ "$1" == "14" ]; then
  test14
  exit 0
fi

if [ "$1" == "15" ]; then
  test15
  exit 0
fi

echo "ERROR: Invalid parm, must be '14' or '15'"
exit 1

