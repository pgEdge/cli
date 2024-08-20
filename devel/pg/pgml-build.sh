
pgmlV=2.9.3
pgV=16.4
cargoV=0.11.3 

pgbin=$PWD/$pgV/bin
export PATH=$pgbin:$PATH

set -x

cargo install cargo-pgrx --version $cargoV

rm -rf postgresml
git clone https://github.com/postgresml/postgresml
cd postgresml/
git checkout v$pgmlV
git submodule update --init --recursive

cargo pgrx init --pg16 $pgbin/pg_config
cd pgml-extension
cargo pgrx package
