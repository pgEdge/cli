FROM rockylinux:8

LABEL maintainer="NDCTL team"

SHELL ["/bin/bash", "-c"]

USER root

RUN dnf update -y \
    && dnf install -y wget curl git sudo python39 python39-devel \
    && dnf clean all \
    && rm -rf /var/cache/yum

RUN useradd pgedge -U -m -d /home/pgedge \
    && echo "pgedge ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers

USER pgedge
WORKDIR /home/pgedge

RUN git clone https://github.com/pgedge/ndctl 
WORKDIR ndctl
RUN ./setupInitial.sh \
    && dnf clean all \
    && rm -rf /var/cache/yum

CMD /bin/bash
