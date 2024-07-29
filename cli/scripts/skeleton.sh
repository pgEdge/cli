#!/bin/bash

#  Copyright 2022-2024 PGEDGE  All rights reserved. #


function install_pgedge {
  ./pgedge install $pgV; 
  ./pgedge start $pgV -y -d demo;
  ./pgedge install spock              -d demo
  ./pgedge install snowflake-$pgV     -d demo
  ./pgedge install lolor-$pgV         -d demo
}


## extensions common to pg15 & pg16
function test_common_exts {

  ./pgedge install hypopg-$pgV        -d demo
  ./pgedge install orafce-$pgV        -d demo
  ##./pgedge install curl-$pgV          -d demo
  ./pgedge install cron-$pgV
  ./pgedge install partman-$pgV       -d demo
  ./pgedge install postgis-$pgV       -d demo
  ./pgedge install vector-$pgV        -d demo
  ./pgedge install audit-$pgV         -d demo
  ./pgedge install hintplan-$pgV      -d demo
  ./pgedge install timescaledb-$pgV   -d demo
  ./pgedge install setuser-$pgV       -d demo
  ./pgedge install permissions-$pgV   -d demo

  ./pgedge install plv8-$pgV          -d demo

  #./pgedge install pljava-$pgV        -d demo

  ## extensions that dont always play nice with others
  # ./pgedge install plprofiler-$pgV
  # ./pgedge install pldebugger-$pgV    -d demo
  # ./pgedge install citus-$pgV         -d demo
}


function test16 {
  install_pgedge

  test_common_exts
}


function test15 {
  install_pgedge
  ./pgedge install foslots-$pgV       -d demo

  test_common_exts

}


function test14 {
  install_pgedge
  ./pgedge install foslots-$pgV       -d demo
}


cd ../..
pgV="pg$1"

if [ "$pgV" == "pg16" ]; then
  test16
  exit 0
fi

if [ "$pgV" == "pg15" ]; then
  test15
  exit 0
fi

if [ "$pgV" == "pg14" ]; then
  test14
  exit 0
fi

echo "ERROR: Invalid parm, must be '14', '15' or '16'"
exit 1

