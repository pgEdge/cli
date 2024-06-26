
# echo ""
# echo "## after-remove.sh "

cd /opt/pgedge
./pgedge stop
sleep 4
rm -rf pg*
rm -rf hub

echo ""
echo "# /opt/pgedge/data has been left intact for the remove manually (if desired).
echo ""

