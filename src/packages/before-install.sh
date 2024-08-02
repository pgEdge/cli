
grp=""
apt --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
  grp="--group"
fi

grep -q "^pgedge:" /etc/passwd >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "## 'pgedge' user already exists"
else
  echo "## adding 'pgedge' user"
  adduser --system $grp --shell /usr/bin/bash pgedge
fi

if [ -d /home/pgedge ]; then
  echo "## home directory '/home/pgedge' already exists"
else
  echo "## creating home directory '/home/pgedge'"
  mkdir /home/pgedge
fi
chown -R pgedge:pgedge /home/pgedge

grep -q "pgedge ALL=(ALL) NOPASSWD: ALL" /etc/sudoers >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "## 'pgedge' user already has passwordless sudo"
else
  echo "## granting 'pgedge' passwordless sudo"
  echo '%pgedge ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
fi
