#!/bin/bash
cd "$(dirname "$0")"

./stopHTTP.sh
cmd="python3 -m http.server"
echo $cmd
cd $OUT
$cmd &
sleep 2

