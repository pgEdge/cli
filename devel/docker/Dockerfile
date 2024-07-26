# create new Debian 12 image
FROM debian
MAINTAINER pgEdge <support@pgedge.com>

ENV TK_V=12.5.1
ENV URL=https://developer.download.nvidia.com/compute/cuda
ENV PFX=cuda-repo-debian12-12-5-local
ENV DEB_F=$PFX_$TK_V-555.42.06-1_amd64.deb

RUN sed -i 's/^Components: main$/& contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
RUN apt -y update

RUN apt -y install software-properties-common
RUN add-apt-repository -y contrib
RUN apt -y update

RUN apt-get -y install wget gawk gcc sqlite3 vim

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN apt-get -y update
RUN apt-get -y install cuda-toolkit-12-5

RUN apt-get install -y nvidia-kernel-open-dkms
RUN apt-get install -y cuda-drivers


#RUN echo "Dockerfile Test on Apache2" > /var/www/html/index.html

EXPOSE 5432
#CMD ["/usr/sbin/apachectl", "-D", "FOREGROUND"]
