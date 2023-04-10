lcl=~/.local/lib/python3.9/site-packages
lib=arm/el8

cp -r $lcl/psycopg*      $lib/.
cp -r $lcl/cffi*         $lib/.
cp -r $lcl/cryptography* $lib/.
cp -r $lcl/nacl*         $lib/.
cp -r $lcl/PyNaCl*       $lib/.
cp -r $lcl/paramiko*     $lib/.
cp -r $lcl/psutil*       $lib/.
cp -r $lcl/pycparser*    $lib/.
cp -r $lcl/resolvelib*   $lib/.

