#!/bin/bash

#  Copyright 2022-2024 PGEDGE  All rights reserved. #


function install_pgedge {
  ./pgedge install $pgV; 
  ./pgedge start $pgV -y -d demo;
  ./pgedge install spock              -d demo
  ./pgedge install snowflake-$pgV     -d demo
  ./pgedge install lolor-$pgV         -d demo
}


## extensions common to pg15, pg16 & pg17
function test_common_17 {
  ./pgedge install cron-$pgV
  ./pgedge install audit-$pgV         -d demo
  ./pgedge install hintplan-$pgV      -d demo

  # ./pgedge install plprofiler-$pgV
  # ./pgedge install pldebugger-$pgV    -d demo
}


## extensions common to pg15 & pg16
function test_common_16 {

  ./pgedge install hypopg-$pgV        -d demo
  ./pgedge install orafce-$pgV        -d demo
  ./pgedge install partman-$pgV       -d demo
  ./pgedge install postgis-$pgV       -d demo
  ./pgedge install vector-$pgV        -d demo
  ./pgedge install timescaledb-$pgV   -d demo
  ./pgedge install setuser-$pgV       -d demo
  ./pgedge install permissions-$pgV   -d demo

  ./pgedge install plv8-$pgV          -d demo

  #./pgedge install pljava-$pgV        -d demo

  ## extensions that dont always play nice with others
  # ./pgedge install citus-$pgV         -d demo
}


function test17 {
  install_pgedge
  test_common_17
}


function test16 {
  install_pgedge
  test_common_16
  test_common_17
}


function test15 {
  install_pgedge
  test_common_16  
  test_common_17
}


function test14 {
  install_pgedge
}


cd ../..
pgV="pg$1"

if [ "$pgV" == "pg17" ]; then
  test17
elif [ "$pgV" == "pg16" ]; then
  test16
elif [ "$pgV" == "pg15" ]; then
  test15
elif [ "$pgV" == "pg14" ]; then
  test14
else
  echo "ERROR: Invalid parm, must be one of '14' thru '17'"
  exit 1
fi

echo "Goodbye!"
exit 0


