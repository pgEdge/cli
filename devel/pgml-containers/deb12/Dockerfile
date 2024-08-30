#FROM docker://nvidia/cuda:12.1.1-devel-ubuntu22.04
FROM docker://debian
ENV PATH="/usr/local/cuda/bin:${PATH}"

RUN apt update && \
	apt install -y \
		lsb-release curl wget  ca-certificates \
		gnupg coreutils sudo openssl \
		vim python3-dev python3-venv python3-pip \
                git wget curl libopenblas-dev

RUN apt-get install -y software-properties-common
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN add-apt-repository contrib
RUN apt-get update
RUN apt-get -y install cuda-toolkit-12-5

#RUN apt-get install -y nvidia-kernel-open-dkms
#RUN apt-get install -y cuda-drivers

ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN useradd -m build  --shell /bin/bash
RUN adduser build sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER build

WORKDIR /home/build 
ENV REPO=http://host.docker.internal:8000
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

ENV VIRTUAL_ENV=/home/build/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY reqs.linux.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

USER build 

#WORKDIR /home/build/pgedge
#COPY install_pgml.py .
#RUN python3 install_pgml.py

RUN mkdir dev
WORKDIR dev
RUN git clone https://github.com/pgedge/cli
WORKDIR cli/devel/setup
RUN /bin/bash -c '/home/build/dev/cli/devel/setup/1a-toolset.sh'
RUN /bin/bash -c '/home/build/dev/cli/devel/setup/1b-bashrc.sh'
RUN echo 'source ~/venv/bin/activate' >> /home/build/.bashrc
RUN . /home/build/.bashrc

RUN /bin/bash -c '/home/build/dev/cli/devel/setup/1c-awscli.sh'
USER root
COPY config /home/build/.aws/.
RUN chown build:build /home/build/.aws/config

USER build
ENV IN=/home/build/dev/in
ENV REGION=us-east-2
ENV BUCKET=s3://pgedge-upstream
RUN /bin/bash -c '/home/build/dev/cli/devel/setup/1d-pull-IN.sh'



EXPOSE 5432


#COPY entrypoint.sh /app/entrypoint.sh
#COPY dashboard.sh /app/dashboard.sh

#COPY --chown=postgres:postgres local_dev.conf /etc/postgresql/15/main/conf.d/01-local_dev.conf
#COPY --chown=postgres:postgres pg_hba.conf /etc/postgresql/15/main/pg_hba.conf

#ENTRYPOINT ["bash", "/bin/bash"]
