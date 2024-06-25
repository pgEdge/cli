
echo ""
echo "## after-install.sh "

chown -R pgedge:pgedge /opt/pgedge

echo ""
echo "1.) Change to the system user 'pgedge'"
echo "      $ sudo su - pgedge"
echo ""
echo "2.) Run the setup command to startup pgedge & create an initial db"
echo "      $ cd /opt/pgedge"
echo "      $ ./pgedge setup -U user -P passwd -d db --autostart"

