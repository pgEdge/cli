#!/bin/bash
cd "$(dirname "$0")"

REMOTE_REPO=s3://pgedge-upstream/REPO

if [ ! -d "local" ]; then
    mkdir "local"
fi

