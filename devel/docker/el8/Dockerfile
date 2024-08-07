FROM docker://rockylinux/rockylinux:8-ubi-init

RUN dnf -y update && \
    dnf -y install epel-release sudo openssh-server \
      python39 python39-devel python39-pip git \
      wget curl pigz sqlite which zip

RUN systemctl enable sshd.service

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
ENV IN=/home/build/dev/in
RUN mkdir -p $IN
ENV OUT=/home/build/dev/out
RUN mkdir  $OUT

WORKDIR $HOME/dev
RUN git clone https://github.com/pgedge/cli
WORKDIR /home/build/dev/cli/devel/setup
RUN  ./1b-bashrc.sh
RUN source /home/build/.bashrc

RUN pip3 install --user --upgrade --no-warn-script-location pip
ENV PATH=$HOME/.local/bin:$PATH
RUN which pip3
RUN ./1c-awscli.sh
RUN cp /tmp/config /home/build/.aws/. && chmod 600 /home/build/.aws/config && rm /tmp/config

USER root

