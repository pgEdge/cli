FROM docker://rockylinux/rockylinux:8-ubi-init

RUN dnf -y update && \
    dnf -y install yum-utils epel-release \
      python39 python39-devel python39-pip \
      git wget curl pigz sqlite which zip

RUN dnf config-manager --set-enabled powertools && \
    dnf -y groupinstall 'development tools'

RUN dnf -y install gcc-toolset-13 \
      dnf-plugins-core \
      perl-devel perl-CPAN perl-JSON perl-App-cpanminus cpan \
      openssh-server

RUN systemctl enable sshd.service

RUN dnf -y --nobest install zlib-devel bzip2-devel lbzip2 \
      openssl-devel libxslt-devel libevent-devel c-ares-devel \
      perl-ExtUtils-Embed pam-devel openldap-devel boost-devel chrpath clang-devel \
      llvm-devel cmake libxml2-devel libedit-devel sqlite-devel \
      *ossp-uuid* openjpeg2-devel libyaml libyaml-devel \
      ncurses-compat-libs systemd-devel unixODBC-devel protobuf-c-devel libyaml-devel \
      lz4-devel libzstd-devel krb5-devel geos-devel proj-devel gdal sqlite-devel \
      @ruby:3.0 ruby-devel rpm-build squashfs-tools java-17-openjdk && \
    yum clean all && rm -rf /var/cache/yum && gem install fpm

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install-rust.sh && \
    chmod 755 install-rust.sh && ./install-rust.sh -y &&  rm install-rust.sh

RUN update-alternatives --set python3 /usr/bin/python3.9

# Create a new user and set the password
RUN dnf -y install sudo && \
    useradd -m build && \
    echo "build:bld" | chpasswd && \
    echo "%build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# picking up the .aws/config file for later use after awscli is installed
COPY ./config /tmp/.
RUN chown build:build /tmp/config

USER build
ENV HOME=/home/build

WORKDIR $HOME
RUN mkdir .ssh && ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa
WORKDIR .ssh
RUN cat id_rsa.pub >> known_hosts

WORKDIR $HOME
RUN python3 -m venv venv
RUN pip3 install --user --upgrade --no-warn-script-location pip

ENV IN=/home/build/dev/in
RUN mkdir -p $IN
ENV OUT=/home/build/dev/out
RUN mkdir  $OUT

WORKDIR $HOME/dev
RUN git clone https://github.com/pgedge/cli
WORKDIR /home/build/dev/cli/devel/setup
RUN  ./1b-bashrc.sh
RUN source /home/build/.bashrc

RUN ./1c-awscli.sh

RUN cp /tmp/config /home/build/.aws/. && chmod 600 /home/build/.aws/config && rm /tmp/config
ENV PATH=$HOME/.local/bin:$PATH
ENV REGION=us-east-2
ENV BUCKET=s3://pgedge-upstream
RUN ./1d-pull-IN.sh

USER root
RUN dnf -y install sudo

