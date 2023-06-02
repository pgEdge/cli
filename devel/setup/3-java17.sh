set -x

jdkV=17
sudo dnf -y install java-$jdkV-openjdk-devel

mavenV=3.9.2
file=apache-maven-$mavenV-bin.tar.gz
url=https://dlcdn.apache.org/maven/maven-3/$mavenV/binaries/$file

rm -f $file
wget $url/$file
tar -xvf $file
rm $file



