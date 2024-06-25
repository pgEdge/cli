
echo ""
echo "## before-install.sh "

adduser pgedge --system
rc=$?
if [ "$rc" == "0" ]; then
  mkdir /home/pgedge
  chown pgedge:pgedge /home/pgedge

  echo '%pgedge ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
fi

