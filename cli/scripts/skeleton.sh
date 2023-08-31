

function test16 {
  pgV=pg16
  ./nodectl install pg16; 
  ./nodectl start pg16 -y -d demo;

  ./nodectl install spock31-$pgV       -d demo
  ./nodectl install hypopg-$pgV        -d demo
  ./nodectl install orafce-$pgV        -d demo
  ./nodectl install curl-$pgV          -d demo
  ./nodectl install cron-$pgV
  ./nodectl install postgis-$pgV       -d demo
  ./nodectl install vector-$pgV        -d demo
}


function test15 {
  pgV=pg15
  ./nodectl install pg15; 
  ./nodectl start pg15 -y -d demo;

  ./nodectl install spock31-$pgV       -d demo
  ./nodectl install hypopg-$pgV        -d demo

  ./nodectl install orafce-$pgV        -d demo
  ./nodectl install curl-$pgV          -d demo
  ./nodectl install partman-$pgV       -d demo
  ./nodectl install cron-$pgV
  ./nodectl install postgis-$pgV       -d demo
  ./nodectl install hintplan-$pgV      -d demo
  ./nodectl install timescaledb-$pgV   -d demo
  ./nodectl install vector-$pgV        -d demo
  ./nodectl install pldebugger-$pgV    -d demo

  #./nodectl install foslots-$pgV       -d demo
  #./nodectl install plprofiler-$pgV

  #./nodectl install decoderbufs-$pgV   -d demo
  #./nodectl install plv8-$pgV          -d demo

  #./nodectl install citus-$pgV         -d demo
  #./nodectl install bulkload-$pg V     -d demo
  #./nodectl install repack-$pgV        -d demo
  #./nodectl install mysqlfdw-$pgV      -d demo
  #./nodectl install mongofdw-$pgV      -d demo
  #./nodectl install oraclefdw-$pgV     -d demo
  #./nodectl install esfdw-$pgV         -d demo
  #./nodectl install multicorn2-$pgV    -d demo
  #./nodectl install hypopg-$pgV        -d demo
}


cd ../..

if [ "$1" == "16" ]; then
  test16
  exit 0
fi

if [ "$1" == "15" ]; then
  test15
  exit 0
fi

echo "ERROR: Invalid parm, must be '15' or '16'"
exit 1

