

echo "## adding pgedge system user"

adduser pgedge --system
rc=$?
if [ "$rc" == "0" ]; then
  mkdir /home/pgedge
  chown pgedge:pgedge /home/pgedge

  echo '%pgedge ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
fi

