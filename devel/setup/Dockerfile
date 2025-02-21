FROM rockylinux/rockylinux:9
RUN touch /etc/hostname

SHELL ["/bin/bash", "-c"]

USER root

ENV install="dnf install -y --allowerasing"
RUN $install dnf-plugins-core
RUN $install python3 python3-pip git wget curl pigz which zip sqlite
RUN $install openssh-server systemd sudo

RUN useradd build  -U -m -d /home/build  \
    && echo "build  ALL=(ALL)  NOPASSWD: ALL" >> /etc/sudoers

USER build
WORKDIR /home/build/dev

RUN git clone https://github.com/pgedge/cli
# Temporary workaround for script behavior
RUN cd cli/devel/setup && bash -x ./10-toolset.sh || true
RUN cd cli/devel/setup && ./20-venv.sh
RUN cd cli/devel/setup && ./30-bashrc.sh
RUN source ~/.bashrc
RUN cd cli/devel/setup && ./40-awscli.sh

CMD /bin/bash