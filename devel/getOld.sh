
rm -rf pgedge
unset REPO
python3 -c "$(curl -fsSL https://pgedge-download.s3.amazonaws.com/REPO/install.py)"
cd pgedge
./nc set GLOBAL REPO http://localhost:8000
./nc info
