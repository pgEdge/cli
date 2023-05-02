#!/bin/bash
cd "$(dirname "$0")"

dir=$NC/devel/pgbin/build
cp -p *.sh $dir/.
cd $NC 
git diff
