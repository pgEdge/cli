
err_msg="ERROR: parm must = 'upstream' or 'download'"

set -x

if [ "$1" == "" ]; then
  echo $err_msg
  exit 1
fi

if [ ! "$1" == "upstream" ] && [ ! "$1" == "download" ]; then
  echo $err_msg
  exit 1
fi

repo=$1

if [ -d pgedge ]; then
  pgedge/nc stop
  rm -rf pgedge
fi

export REPO=https://pgedge-$repo.s3.amazonaws.com/REPO

nc=pgedge
if [ "$repo" == "download" ]; then
  nc=nc
fi


rm -f install.py
wget $REPO/install.py
python3 install.py
rm install.py

cd pgedge
./$nc set GLOBAL REPO http://localhost:8000
./$nc info
