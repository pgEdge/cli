#!/bin/bash
cd "$(dirname "$0")"

cmd="./pgedge setup pgedge"

if [ "$#" == "0" ]; then
   $cmd --help
else
   $cmd "$@"
fi


