#!/bin/bash
cd "$(dirname "$0")"

./copy-to-upstream.sh $1

./copy-to-download.sh $1

