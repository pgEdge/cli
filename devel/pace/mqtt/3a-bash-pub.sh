set -x

if [ "$1" == "" ];then
  msg="info"
else
  msg="$1"
fi

echo "Terminal #2 (Publisher)"
mosquitto_pub -h localhost -t nodectl -m "$msg"

