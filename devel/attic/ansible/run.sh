source env.sh

if [ -d pgedge ]; then
  pgedge/nc cluster destroy cl1
  rm -rf pgedge
fi

rm -f install.py
wget $REPO/install.py
rc=$?
echo "(rc = $rc)"
if [ ! "$rc" == "0" ]; then
  exit $rc
fi

python3 install.py

pgedge/nc cluster create-local cl1 1 --pg=15 --app=pgbench
rc=$?
echo "(rc = $rc)"
exit $rc
