FROM docker://nvidia/cuda:12.5.1-devel-ubuntu22.04
ENV PATH="/usr/local/cuda/bin:${PATH}"
RUN apt update && \
	apt install -y \
		lsb-release curl wget  ca-certificates \
		gnupg coreutils sudo openssl \
		vim python3-dev python3-venv python3-pip \
                git wget curl

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m mledge --shell /bin/bash
RUN adduser mledge sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER mledge

WORKDIR /home/mledge
ENV REPO=http://192.168.1.193:8000
RUN wget $REPO/install.py
RUN python3 install.py

ENV VIRTUAL_ENV=/home/mledge/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install gpustat

WORKDIR /home/mledge/pgedge


#RUN apt update -y && apt install git postgresml-15 postgresml-dashboard -y
#RUN git clone --branch v0.5.0 https://github.com/pgvector/pgvector && \
#cd pgvector && \
#echo "trusted = true" >> vector.control && \
#	make && \
#	make install

#COPY entrypoint.sh /app/entrypoint.sh
#COPY dashboard.sh /app/dashboard.sh

#COPY --chown=postgres:postgres local_dev.conf /etc/postgresql/15/main/conf.d/01-local_dev.conf
#COPY --chown=postgres:postgres pg_hba.conf /etc/postgresql/15/main/pg_hba.conf

#ENTRYPOINT ["bash", "/bin/bash"]
