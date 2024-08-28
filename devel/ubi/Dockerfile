FROM docker://redhat/ubi9:latest

RUN dnf -y  update && dnf remove -y subscription-manager dnf-plugin-subscription-manager

ENV install="dnf install -y --allowerasing"
RUN $install python3 python3-pip git wget curl pigz which zip sqlite
RUN $install openssh-server systemd

RUN adduser --home-dir /home/pgedge --shell /bin/bash  pgedge
RUN echo '%pgedge ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER pgedge
WORKDIR /home/pgedge
ENV REPO=https://pgedge-upstream.s3.amazonaws.com/REPO
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py

EXPOSE 22



