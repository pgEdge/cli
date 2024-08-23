
R_DOWNLOAD=https://pgedge-download.s3.amazonaws.com/REPO
R_UPSTREAM=https://pgedge-upstream.s3.amazonaws.com/REPO
R_DEVEL=https://pgedge-devel.s3.amazonaws.com/REPO
R_LOCALHOST=http://localhost:8000

if [ -d pgedge ]; then
  pgedge/pgedge stop
  sleep 2
  rm -rf pgedge
fi

export REPO=$R_DOWNLOAD
python3 -c "$(curl -fsSL $REPO/install.py)"

set -x

cd pgedge
./pgedge info

./pgedge install pg16 --disabled
./pgedge install spock33 --disabled
./pgedge install snowflake --disabled
./pgedge stop 

./pgedge set GLOBAL REPO $R_LOCALHOST
./pgedge info
