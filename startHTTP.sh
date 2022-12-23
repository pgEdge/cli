
./stopHTTP.sh
 cmd="python3 -m http.server"
echo $cmd
cd $OUT
$cmd &

