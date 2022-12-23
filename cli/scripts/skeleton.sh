

function test14 {
  pgV=pg14
  ./io install pg14; 
  ./io start pg14 -y -d demo;

  ## Citus must be installed first before any other extension
  ./io install citus-$pgV

  ./io install audit-$pgV         -d demo
  ./io install hintplan-$pgV      -d demo
  ./io install timescaledb-$pgV   -d demo
}


function test15 {
  pgV=pg15
  ./io install pg15; 
  ./io start pg15 -y -d demo;

  ./io install multicorn2-$pgV    -d demo
  ./io install plprofiler-$pgV    -d demo
  ./io install pldebugger-$pgV    -d demo

  ./io install repack-$pgV        -d demo
  ./io install orafce-$pgV        -d demo
  ./io install spock-$pgV        -d demo

  ./io install bulkload-$pgV      -d demo
  ./io install partman-$pgV       -d demo
  ./io install cron-$pgV

  #./io install plv8-$pgV          -d demo

  if [ `arch` == "aarch64" ]; then
    ./io install postgis-$pgV      -d demo
  #else
  #  ./io install mysqlfdw-$pgV     -d demo
  #  ./io install mongofdw-$pgV     -d demo
  #  ./io install oraclefdw-$pgV    -d demo
  #  ./io install esfdw-$pgV        -d demo
  fi

  #./io install decoderbufs-$pgV   -d demo
  #./io install hypopg-$pgV        -d demo
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

