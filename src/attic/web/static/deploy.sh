
www=/var/www/html
set -x
sudo cp  html/*.html $www/.
cd html
sudo cp -r img  $www/
sudo cp -r projects $www/

