#!/bin/bash
cd "$(dirname "$0")"

./ctl --deprecate-nc "$@"
