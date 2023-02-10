
old_h=2.20
new_h=2.21

srchNrplc() {
  file=$1
  echo "# changing: $file"
  if [ ! -f "$file" ]; then
    echo "  ERROR: missing $file"
    return
  fi

  grep $old_h $file > /dev/null 2>&1
  rc=$?
  if [ "$rc" == "0" ]; then
    sed -i -e "s/$old_h/$new_h/g" $file
  else
    echo "  ERROR: missing $old_h from $file"
  fi

  echo " "
  return
}
    

echo "##bumpHub from $old_h to $new_h"

srchNrplc "env.sh"
srchNrplc "$CLI/util.py"
srchNrplc "$CLI/install.py"
srchNrplc "src/conf/versions.sql"
