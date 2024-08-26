
R_DOWNLOAD=https://pgedge-download.s3.amazonaws.com/REPO
R_UPSTREAM=https://pgedge-upstream.s3.amazonaws.com/REPO
R_DEVEL=https://pgedge-devel.s3.amazonaws.com/REPO
R_LOCALHOST=http://localhost:8000

set -x

if [ -d pgedge ]; then
  pgedge/pgedge stop
  bakup-pgedge/pgedge stop
  rm -rf pgedge
fi

export REPO=$R_DOWNLOAD
python3 -c "$(curl -fsSL $REPO/install.py)"

cd pgedge
./pgedge info

./pgedge setup $CONN
./pgedge stop

export REPO=$R_LOCALHOST
#export REPO=$R_DEVEL
./pgedge set GLOBAL REPO $REPO

pwd
./pgedge info

cd ..

## make the backup dir
rm -rf bakup-pgedge
cp -r pgedge bakup-pgedge
