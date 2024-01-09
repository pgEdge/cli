#!/bin/bash
cd "$(dirname "$0")"

dir=$DEVEL/pgbin/build
cp -p *.sh $dir/.
cd $CT 
git diff
