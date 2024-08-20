

source ./pgml-env.sh

set -e
set -x

ver=$pgmlV-1
base=postgresml/pgml-extension/target/release/pgml-pg16/home/$USER/dev/cli/devel/pg/$pgV 
dir=pgml-pg16-$ver-$plat

rm -rf $dir*
mkdir $dir

cp -r $base/* $dir

tgz=$dir.tgz
tar czf $tgz $dir
rm -rf $dir

cp $tgz $IN/postgres/pgml/.
rm $tgz

echo "Goodbye!"
exit 0


