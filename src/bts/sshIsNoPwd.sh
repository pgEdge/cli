
p_host=$1
if [ "$p_host" == "" ]; then
  p_host=localhost
fi

echo ""
echo "## isPasswdLessSSH.sh to $p_host ######################"

ssh -o PasswordAuthentication=no  -o BatchMode=yes $p_host exit &>/dev/null
rc=$?
if [ "$rc" == "0" ]; then
  echo "Passwordless SSH is working."
  exit 0
fi

echo "ERROR: Passwordless SSH is NOT working."
exit 1

