FROM rockylinux/rockylinux:9
RUN touch /etc/hostname
RUN dnf -y update && dnf remove -y subscription-manager dnf-plugin-subscription-manager

ENV install="dnf install -y --allowerasing"
RUN $install python3 python3-pip git wget curl pigz which zip sqlite
RUN $install openssh-server systemd sudo


RUN adduser --home-dir /home/pgedge --shell /bin/bash  pgedge
RUN echo '%pgedge ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN rm -f /var/run/nologin
RUN sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
RUN ssh-keygen -A
RUN /usr/sbin/sshd

USER pgedge
WORKDIR /home/pgedge
RUN mkdir -p .ssh/
ADD id_rsa.pub /home/pgedge/.ssh/id_rsa.pub
ADD id_rsa /home/pgedge/.ssh/id_rsa

RUN cat /home/pgedge/.ssh/id_rsa.pub >> /home/pgedge/.ssh/authorized_keys
RUN chmod 600 /home/pgedge/.ssh/authorized_keys
RUN chmod 700 /home/pgedge/.ssh/

RUN sudo chown pgedge:pgedge /home/pgedge/.ssh/id_rsa
RUN sudo chmod 600 /home/pgedge/.ssh/id_rsa
ENV REPO=https://pgedge-upstream.s3.amazonaws.com/REPO
RUN wget $REPO/install.py
RUN python3 install.py
RUN rm install.py


USER root
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]

