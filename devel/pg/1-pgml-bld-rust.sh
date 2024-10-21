
source ./pgml-env.sh

pgbin=$PWD/$pgV/bin
export PATH=$pgbin:$PATH
export PGRX_IGNORE_RUST_VERSIONS=1

set -e
set -x

cargo install cargo-pgrx --version $cargoV --force

dir=pgml-$ver
file=$dir.tar.gz
rm -rf $dir
rm -f $file

cp $IN/$file .
tar -xf $file
rm $file
mv $dir pgml
cd pgml


cargo pgrx init --pg$pgMajorV $pgbin/pg_config
cd pgml-extension
cargo pgrx package

echo "Goodbye!"
exit 0
