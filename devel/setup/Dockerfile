FROM rockylinux:8

SHELL ["/bin/bash", "-c"]

USER root

RUN dnf update -y \
    && dnf install -y wget curl git sudo \
    && dnf clean all \
    && rm -rf /var/cache/yum

RUN useradd build  -U -m -d /home/build  \
    && echo "build  ALL=(ALL)  NOPASSWD: ALL" >> /etc/sudoers

USER build
WORKDIR /home/build

RUN git clone https://github.com/pgedge/cli
WORKDIR cli/devel/setup
RUN ./1-cli.sh  \
    && dnf clean all \
    && rm -rf /var/cache/yum

CMD /bin/bash
