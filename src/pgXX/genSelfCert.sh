
rm -f server.key
rm -f server.crt

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/C=US/ST=Virginia/L=Alexandria/O=self/OU=signed/CN=localhost"\
  -keyout server.key -out server.crt

cp server.crt root.crt

