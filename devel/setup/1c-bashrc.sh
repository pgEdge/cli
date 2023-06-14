
if [ -f ~/.bashrc ]; then
  bf=~/.bashrc
else
  bf=~/.bash_profile
fi

grep NC $bf > /dev/null 2>&1
rc=$?
if [ "$rc" == "0" ]; then
  echo "Your $bf appears to already be configured for NodeCtl"
else
  cat bash_profile >> $bf
  echo "# run \"source $bf\" to load revised profile without re-booting"
fi

