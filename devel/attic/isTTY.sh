
export isTTY="False"
if tty -s; then
  export isTTY="True"
fi

echo "isTTY = $isTTY"

