now=`date --iso-8601=ns`

echo "" >> pgcat.log
echo "$now - stopping pgcat" >> pgcat.log

echo "stopping pgcat"
pkill --echo pgcat | tee -a pgcat.log
