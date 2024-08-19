FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV INSTALL="apt-get install -y"
ENV USER=build
ENV HOME=/home/$USER
ENV IN=$HOME/dev/in
ENV OUT=$HOME/dev/out

RUN apt-get update && \
    $INSTALL apt python3 python3-pip pigz sudo zip wget curl sqlite3 git && \
    $INSTALL openssh-server systemd

RUN useradd -m $USER && \
    echo "$USER:bld" | chpasswd && \
    echo "%$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# picking up the .aws/config file for later use after awscli is installed
COPY ./config /tmp/.
RUN chown $USER:$USER /tmp/config

USER $USER

WORKDIR $HOME
RUN mkdir .ssh && ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa
WORKDIR .ssh
RUN cat id_rsa.pub >> known_hosts

WORKDIR $HOME
RUN mkdir -p $IN
RUN mkdir  $OUT

WORKDIR $HOME/dev
RUN git clone https://github.com/pgedge/cli
WORKDIR /home/build/dev/cli/devel/setup
RUN ./1b-bashrc.sh
RUN . $HOME/.bashrc

RUN pip3 install --user --upgrade --no-warn-script-location pip
ENV PATH=$HOME/.local/bin:$PATH
RUN ./1c-awscli.sh
RUN cp /tmp/config $HOME/.aws/. && chmod 600 $HOME/.aws/config && rm /tmp/config

USER root


#CMD [ "/lib/systemd/systemd" ]

