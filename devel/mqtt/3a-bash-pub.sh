source ./env.sh

if [ "$1" == "" ];then
  echo "ERROR: 'msg' is the one required parm"
  exit 1
fi

msg="$1"

set -x

mosquitto_pub -h $BROKER_HOST -p $BROKER_PORT -t $TOPIC  -m "$msg"

