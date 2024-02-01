#!/bin/bash
cd "$(dirname "$0")"

cmd="./pgedge setup pgedge"

if [$# -eq 0]; 
   $cmd --help
else
   $cmd "$@"
fi


