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

COPY kirk-config.sh /home/pgedge/.kirk.conf
RUN chown pgedge:sudo /home/pgedge/.kirk.conf
RUN chmod 700 /home/pgedge/.kirk.conf

#ARG DATA_DIR="/data/pgdata"
#RUN mkdir -p ${DATA_DIR} \
#    && chown -R pgedge:sudo /data \
#    && chmod 750 /data ${DATA_DIR}

ARG CACHEBUST=1

USER pgedge
WORKDIR /opt

ENV REPO=http://172.17.0.1:8000
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

WORKDIR /opt/pgedge
RUN ./pgedge install pg16 pg17 kirk --disabled
RUN ./pgedge install spock40-pg16 snowflake-pg16  --disabled
RUN ./pgedge install spock40-pg17 snowflake-pg17  --disabled

EXPOSE 5432

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
