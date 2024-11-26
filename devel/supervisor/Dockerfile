FROM ubuntu:22.04

ARG USER=pgedge
ARG CMD=pgedge
ARG HOME=/home/$USER
ARG LOCT=/opt
ARG REPO=http://172.17.0.1:8000
ARG KIRK_CONF=$HOME/.kirk.conf

RUN apt update && \
	apt install -y supervisor wget

RUN apt-get -qq install --no-install-recommends  vim > /dev/null

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m $USER --shell /bin/bash
RUN adduser $USER sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN chown $USER:sudo /opt
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY kirk-config.sh $KIRK_CONF
RUN chown pgedge:sudo $KIRK_CONF
RUN chmod 700 $KIRK_CONF

USER $USER 
WORKDIR $LOCT

RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

WORKDIR $LOCT/pgedge
RUN ./$CMD install pg16 kirk --disabled
RUN ./$CMD install spock40-pg16 snowflake-pg16  --disabled

EXPOSE 5432

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
