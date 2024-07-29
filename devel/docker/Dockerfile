# create new Debian 12 image
FROM debian
MAINTAINER pgEdge <support@pgedge.com>

ENV TK_V=12.5.1
ENV NVIDIA_URL=https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64
ENV PFX=cuda-repo-debian12-12-5-local
ENV DEB_F=$PFX_$TK_V-555.42.06-1_amd64.deb

ENV PGML_V=2.9.3
ENV PGML_URL=https://github.com/postgresml/postgresml/archive/refs/tags

RUN sed -i 's/^Components: main$/& contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
RUN apt -y update

RUN apt -y install software-properties-common
RUN add-apt-repository -y contrib
RUN apt -y update

RUN apt-get -y install curl wget gawk gcc sqlite3 vim

RUN wget $NVIDIA_URL/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN apt-get -y update
RUN apt-get -y install cuda-toolkit-12-5

RUN apt-get install -y nvidia-kernel-open-dkms
RUN apt-get install -y cuda-drivers

RUN apt-get install -y python3 python3-dev python3-pip python3-venv
ENV VIRT_ENV=/opt/pgml-venv
RUN python3 -m venv $VIRT_ENV
ENV PATH=$VIRT_ENV/bin:$PATH
RUN pip3 install pip --upgrade

RUN wget $PGML_URL/v$PGML_V.tar.gz
RUN tar -xf v$PGML_V.tar.gz
RUN rm -r v$PGML_V.tar.gz

RUN pip3 install -r postgresml-$PGML_V/pgml-extension/requirements.linux.txt

RUN mkdir -p /opt/pgedge
RUN useradd -ms /bin/bash pgedge 
RUN chown pgedge:pgedge /opt
RUN chown pgedge:pgedge /opt/pgedge
USER pgedge 
WORKDIR /opt

ENV REPO=https://pgedge-upstream.s3.amazonaws.com/REPO
RUN python3 -c "$(curl -fsSL $REPO/install.py)"
WORKDIR /opt/pgedge
RUN ./pgedge install pg16 --start
RUN ./pgedge tune pg16
RUN ./pgedge install spock40 snowflake 
RUN ./pgedge install lolor --disabled

EXPOSE 5432
#CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
