

function test16 {
  pgV=pg16
  ./ctl install pg16; 
  ./ctl start pg16 -y -d demo;

  ./ctl install spock31-$pgV       -d demo
  ./ctl install hypopg-$pgV        -d demo
  ./ctl install orafce-$pgV        -d demo
  ./ctl install curl-$pgV          -d demo
  ./ctl install cron-$pgV
  ./ctl install postgis-$pgV       -d demo
  ./ctl install vector-$pgV        -d demo
  ./ctl install audit-$pgV         -d demo
  ./ctl install plv8-$pgV          -d demo
  ./ctl install hintplan-$pgV      -d demo
  ./ctl install plprofiler-$pgV
}


function test15 {
  pgV=pg15
  ./ctl install pg15; 
  ./ctl start pg15 -y -d demo;

  ./ctl install spock31-$pgV       -d demo
  ./ctl install hypopg-$pgV        -d demo

  ./ctl install orafce-$pgV        -d demo
  ./ctl install curl-$pgV          -d demo
  ./ctl install partman-$pgV       -d demo
  ./ctl install cron-$pgV
  ./ctl install postgis-$pgV       -d demo
  ./ctl install hintplan-$pgV      -d demo
  ./ctl install timescaledb-$pgV   -d demo
  ./ctl install vector-$pgV        -d demo
  ./ctl install pldebugger-$pgV    -d demo

  ./ctl install plv8-$pgV          -d demo
  ./ctl install plprofiler-$pgV

  #./ctl install decoderbufs-$pgV   -d demo

  #./ctl install citus-$pgV         -d demo
  #./ctl install bulkload-$pg V     -d demo
  #./ctl install repack-$pgV        -d demo
  #./ctl install mysqlfdw-$pgV      -d demo
  #./ctl install mongofdw-$pgV      -d demo
  #./ctl install oraclefdw-$pgV     -d demo
  #./ctl install esfdw-$pgV         -d demo
  #./ctl install multicorn2-$pgV    -d demo
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

