FROM docker://nvidia/cuda:12.5.1-devel-ubuntu22.04
ENV PATH="/usr/local/cuda/bin:${PATH}"

RUN apt update && \
	apt install -y \
		lsb-release curl wget  ca-certificates \
		gnupg coreutils sudo openssl \
		vim python3-dev python3-venv python3-pip \
                git wget curl sqlite libopenblas-dev

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m mledge --shell /bin/bash
RUN adduser mledge sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER mledge

WORKDIR /home/mledge
ENV REPO=http://host.docker.internal:8000
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

ENV VIRTUAL_ENV=/home/mledge/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/.
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /home/mledge/pgedge
COPY install_pgml.py .
RUN python3 install_pgml.py


#COPY entrypoint.sh /app/entrypoint.sh
#COPY dashboard.sh /app/dashboard.sh

#COPY --chown=postgres:postgres local_dev.conf /etc/postgresql/15/main/conf.d/01-local_dev.conf
#COPY --chown=postgres:postgres pg_hba.conf /etc/postgresql/15/main/pg_hba.conf

#ENTRYPOINT ["bash", "/bin/bash"]
