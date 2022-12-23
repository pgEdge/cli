pid=`ps aux | grep [h]ttp.server | awk '{print $2}'`

if [ "$pid" > " " ]; then
  echo "killing ($pid)"
  kill -9 $pid > /dev/null 2>&1
else
  echo "http.server not running"
fi


