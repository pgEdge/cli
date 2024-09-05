FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV INSTALL="apt-get install -y"
ENV USER=build
ENV HOME=/home/$USER
ENV IN=$HOME/dev/in
ENV OUT=$HOME/dev/out
ENV REGION=us-east-2
ENV BUCKET=s3://pgedge-upstream

RUN apt-get update && \
    $INSTALL apt python3 python3-pip python3-dev python3-venv \
      pigz sudo zip wget curl sqlite3 git vim \
      build-essential

#RUN $INSTALL openssh-server systemd

RUN useradd -m $USER --shell /bin/bash && \
    echo "$USER:bld" | chpasswd && \
    echo "%$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# picking up the .aws/config file for later use after awscli is installed
COPY ./config /tmp/.
RUN chown $USER:$USER /tmp/config

USER $USER

WORKDIR $HOME
RUN mkdir -p $IN
RUN mkdir  $OUT
RUN python3 -m venv venv

#RUN mkdir .ssh && ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa
#WORKDIR .ssh
#RUN cat id_rsa.pub >> known_hosts

#WORKDIR $HOME



WORKDIR $HOME/dev
RUN git clone https://github.com/pgedge/cli
ENV WD=/home/build/dev/cli/devel/setup
WORKDIR $WD
RUN cat bash_profile >> $HOME/.bashrc
RUN echo "source ~/venv/bin/activate" >> $HOME/.bashrc
RUN . $HOME/.bashrc
RUN which pip3
RUN ~/venv/bin/pip3 install awscli

#RUN pip3 install --user --upgrade --no-warn-script-location pip
#ENV PATH=$HOME/.local/bin:$PATH
#RUN ./1c-awscli.sh
RUN mkdir $HOME/.aws
RUN cp /tmp/config $HOME/.aws/. && chmod 600 $HOME/.aws/config && rm /tmp/config

RUN ./1d-pull-IN.sh 

#USER root


#CMD [ "/bin/bash" ]

