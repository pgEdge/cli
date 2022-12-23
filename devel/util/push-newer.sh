
if [ $# != 2 ]; then
  echo "invalid parms, must be two"
  exit 1
fi

newerthan=$1
echo "newerthan=$newerthan"
hist_dir=$HIST/$2
echo "hist_dir=$hist_dir"

cmd="mkdir $hist_dir"
echo "# $cmd"
$cmd
rc=$?
if [ "$rc" != "0" ]; then
  echo "ERROR: creating $hist_dir"
  exit 1
fi

cmd="./copy-newer.sh $1 $2"
echo "# $cmd"
$cmd
rc=$?
if [ "$rc" != "0" ]; then
  echo "ERROR: IN copy-newer.sh"
  exit 1
fi

read -p "hit <ENTER> to continue"
cmd="./copy-to-s3.sh $2"
echo "# $cmd"
$cmd
rc=$?
exit $rc

