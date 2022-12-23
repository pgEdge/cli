
source buildSrc.sh

#cd /opt
#RAPIDJSON_VERSION=1.1.0
#wget https://github.com/Tencent/rapidjson/archive/refs/tags/v${RAPIDJSON_VERSION}.tar.gz
#tar xzvf v${RAPIDJSON_VERSION}.tar.gz
#rm v${RAPIDJSON_VERSION}.tar.gz
#ln -s rapidjson-${RAPIDJSON_VERSION} rapidjson

BANNER="LIBKRDKAFKA - kafka client library"
v=1.8.2
d=librdkafka-$v
f=v$v.tar.gz
u=https://github.com/edenhill/librdkafka/archive/refs/tags
#buildSrc $v $d $f $u  ./configure 

BANNER="PROTOBUF-CPP - Protobuf library for c++"
v=3.19.4
d=protobuf-$v
f=v$v.tar.gz
u=https://github.com/protocolbuffers/protobuf/archive/refs/tags
buildSrc $v $d $f $u  "./autogen.sh"

exit

cd /opt
wget https://github.com/edenhill/librdkafka/archive/refs/tags/v${LIBRDKAFKA_VERSION}.tar.gz
tar xzvf v${LIBRDKAFKA_VERSION}.tar.gz
rm v${LIBRDKAFKA_VERSION}.tar.gz
cd /opt/librdkafka-${LIBRDKAFKA_VERSION}
./configure --prefix=/opt/librdkafka
make
make install

cd /opt
wget https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOBUF_VERSION}/protobuf-cpp-${PROTOBUF_VERSION}.tar.gz
tar xzvf protobuf-cpp-${PROTOBUF_VERSION}.tar.gz
rm protobuf-cpp-${PROTOBUF_VERSION}.tar.gz
cd /opt/protobuf-${PROTOBUF_VERSION}
./configure --prefix=/opt/protobuf
make
make install

