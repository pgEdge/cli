
set -x

keyDir=/etc/ssl/private
certDir=/etc/ssl/certs
keyNm=nginx-selfsigned

sudo mkdir -p $keyDir

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/C=US/ST=Virginia/L=Alexandria/O=self/OU=signed/CN=localhost"\
  -keyout $keyDir/$keyNm.key -out $certDir/$keyNm.crt

sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 512

snipDir=/etc/nginx/snippets
sudo mkdir -p $snipDir
sudo cp init/self-signed.conf $snipDir/.
sudo cp init/ssl-params.conf $snipDir/.

sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old
sudo cp init/nginx.conf /etc/nginx/.

sudo cp init/index.html /usr/share/nginx/html/.

sudo systemctl restart nginx

wait 2
sudo systemctl status nginx --no-pager

