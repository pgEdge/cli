
set -x

plat=arm
if [ `arch` == "x86_64" ]; then
  plat="amd"
fi

ver=2.9.3-1
base=postgresml/pgml-extension/target/release/pgml-pg16/home/build/dev/cli/devel/pg/16.4
dir=pgml-pg16-$ver-$plat

rm -rf $dir*
mkdir $dir

cp -r $base/* $dir

tgz=$dir.tgz
tar czf $tgz $dir
rm -rf $dir

cp $tgz $IN/postgres/pgml/.
rm $tgz




