set -x

## declare an array variable
declare -a arr=("ls -l $HOME" "echo hello")

## now loop through the above array
for i in "${arr[@]}"
do
   echo ""$i""
   `$i`
done

