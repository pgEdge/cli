
source ./pgml-env.sh

pgbin=$PWD/$pgV/bin
export PATH=$pgbin:$PATH
export PGRX_IGNORE_RUST_VERSIONS=1

set -e
set -x

cargo install cargo-pgrx --version $cargoV --force

rm -rf postgresml
git clone https://github.com/postgresml/postgresml
cd postgresml/
git checkout v$pgmlV
git submodule update --init --recursive

cargo pgrx init --pg$pgMajorV $pgbin/pg_config
cd pgml-extension
cargo pgrx package

echo "Goodbye!"
exit 0
