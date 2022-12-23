PROTOBUF_VERSION=3.19.4
RAPIDJSON_VERSION=1.1.0
LIBRDKAFKA_VERSION=1.8.2

cd /opt
wget https://github.com/Tencent/rapidjson/archive/refs/tags/v${RAPIDJSON_VERSION}.tar.gz
tar xzvf v${RAPIDJSON_VERSION}.tar.gz
rm v${RAPIDJSON_VERSION}.tar.gz
ln -s rapidjson-${RAPIDJSON_VERSION} rapidjson

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

