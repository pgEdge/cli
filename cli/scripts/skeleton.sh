

function test14 {
  pgV=pg14
  ./nc install pg14; 
  ./nc start pg14 -y -d demo;

  ./nc install audit-$pgV         -d demo
  ./nc install timescaledb-$pgV   -d demo
}


function test15 {
  pgV=pg15
  ./nc install pg15; 
  ./nc start pg15 -y -d demo;

  ./nc install plprofiler-$pgV
  ./nc install spock-$pgV         -d demo
  ./nc install pldebugger-$pgV    -d demo

  ./nc install repack-$pgV        -d demo
  ./nc install orafce-$pgV        -d demo
  ./nc install partman-$pgV       -d demo
  ./nc install cron-$pgV

  #./nc install bulkload-$pgV      -d demo

  #./nc install plv8-$pgV          -d demo

  if [ `arch` == "aarch64" ]; then
    ./nc install postgis-$pgV      -d demo
  #else
  #  ./nc install mysqlfdw-$pgV     -d demo
  #  ./nc install mongofdw-$pgV     -d demo
  #  ./nc install oraclefdw-$pgV    -d demo
  #  ./nc install esfdw-$pgV        -d demo

  ./nc install multicorn2-$pgV    -d demo
  ./nc install hintplan-$pgV      -d demo
  #./nc install citus-$pgV         -d demo

  fi

  #./nc install decoderbufs-$pgV   -d demo
  #./nc install hypopg-$pgV        -d demo
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

