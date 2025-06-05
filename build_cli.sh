source ./env.sh
rm -f $OUT/hub-$hubV*
rm -f $OUT/$bundle-cli-$hubV*
./build.sh -X posix -c $bundle-cli -N $hubV

exit 0