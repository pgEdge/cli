
set -xe

cd postgresml/pgml-extension

rm -rf pgml-venv

python3 -m venv pgml-venv
set +x
source pgml-venv/bin/activate
set -x

pip3 install -r requirements.txt

