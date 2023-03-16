now=`date --iso-8601=ns`

echo "" >> pgcat.log
echo "starting pgcat"

pkill --echo pgcat | tee -a pgcat.log

echo "$now - starting pgcat" >> pgcat.log

./pgcat -d pgcat.toml >> pgcat.log 2>&1  &
