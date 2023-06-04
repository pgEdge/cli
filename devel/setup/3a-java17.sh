set -x

jdkV=17
sudo dnf -y install java-$jdkV-openjdk-devel

mavenV=3.9.2
dir=apache-maven-$mavenV
file=$dir-bin.tar.gz
url=https://dlcdn.apache.org/maven/maven-3/$mavenV/binaries

rm -f $file
wget $url/$file
sudo mv $file /opt/.
cd /opt
sudo tar -xf $file
sudo rm $file
ls -l $dir

