
if [ ! -f ~/.ssh/id_rsa ]; then
  ssh-keygen -t rsa -q -f "$HOME/.ssh/id_rsa" -N ""
fi

ssh-copy-id localhost

