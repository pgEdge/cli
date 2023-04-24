FROM rockylinux:8

LABEL maintainer="NODECTL team"

SHELL ["/bin/bash", "-c"]

USER root

RUN dnf update -y \
    && dnf install -y wget curl git sudo python39 python39-devel \
    && dnf clean all \
    && rm -rf /var/cache/yum

RUN useradd build  -U -m -d /home/build  \
    && echo "build  ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers

USER build
WORKDIR /home/build

RUN git clone https://github.com/pgedge/nodectl 
WORKDIR nodectl
RUN ./setupInitial.sh \
    && dnf clean all \
    && rm -rf /var/cache/yum

CMD /bin/bash
