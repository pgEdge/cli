
py3V-`python3 --version`
rc=$?
if [ "$rc" 
pipV=`pip3 --version`
echo "pipV = $pipV"

rm -f get-pip.py
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py
