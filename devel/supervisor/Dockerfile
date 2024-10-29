FROM ubuntu:22.04

RUN apt update && \
	apt install -y supervisor wget

RUN apt-get -qq install --no-install-recommends  vim > /dev/null

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m pgedge --shell /bin/bash
RUN adduser pgedge sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN chown pgedge:sudo /opt
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ARG CACHEBUST=1

USER pgedge
WORKDIR /opt

ENV REPO=http://172.17.0.1:8000
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

WORKDIR /opt/pgedge
RUN ./pgedge setup -U denis -P lussier -d db1 
RUN ./pgedge stop

EXPOSE 5432

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]





