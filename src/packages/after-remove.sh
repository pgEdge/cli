
edg=/opt/pgedge

echo ""
echo "# $edg/data is being left intact to remove manually (if desired)."
echo ""

$edg/pgedge stop
sleep 4
rm -rf $edg/pg*
rm -rf $edg/hub
