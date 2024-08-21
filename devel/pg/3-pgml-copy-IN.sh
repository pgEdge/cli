

source ./pgml-env.sh

set -xe

ver=$pgmlV-1
pgml_ext=postgresml/pgml-extension
base=$pgml_ext/target/release/$pgmlXX/home/$USER/dev/cli/devel/pg/$pgV 
dir=$pgmlXX-$ver-$plat

rm -rf $dir*
mkdir $dir

cp -r $base/* $dir
cp -r $pgml_ext/pgml-venv $dir

tgz=$dir.tgz
tar cf - $dir | pigz > $tgz
rm -rf $dir

cp $tgz $IN/postgres/pgml/.
rm $tgz

echo "Goodbye!"
exit 0


