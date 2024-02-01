#!/bin/bash
cd "$(dirname "$0")"

./pgedge --deprecate-nc "$@"
