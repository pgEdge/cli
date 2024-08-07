FROM docker://rockylinux/rockylinux:8-ubi-init

RUN yum -y update && \
    yum -y install yum-utils epel-release

RUN yum -y install python39 python39-devel python39-pip

RUN dnf -y install git wget curl pigz sqlite which zip

#RUN dnf config-manager --set-enabled powertools
#RUN dnf -y groupinstall 'development tools'
#RUN dnf -y install gcc-toolset-13
#RUN dnf -y install dnf-plugins-core 

#RUN dnf -y install perl-devel perl-CPAN perl-JSON perl-App-cpanminus && \
#    dnf -y install cpan

#RUN dnf -y install httpd
#RUN systemctl enable httpd.service

RUN dnf -y install openssh-server
RUN systemctl enable sshd.service

#RUN dnf -y --nobest install zlib-devel bzip2-devel lbzip2 \
#      openssl-devel libxslt-devel libevent-devel c-ares-devel \
#      perl-ExtUtils-Embed pam-devel openldap-devel boost-devel chrpath clang-devel \
#      llvm-devel cmake libxml2-devel libedit-devel sqlite-devel \
#      *ossp-uuid* openjpeg2-devel libyaml libyaml-devel \
#      ncurses-compat-libs systemd-devel unixODBC-devel protobuf-c-devel libyaml-devel \
#      lz4-devel libzstd-devel krb5-devel geos-devel proj-devel gdal sqlite-devel \
#      @ruby:3.0 ruby-devel rpm-build squashfs-tools && \
#    gem install fpm

#RUN dnf -y install java-17-openjdk && yum clean all && rm -rf /var/cache/yum

#RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install-rust.sh 
#RUN chmod 755 install-rust.sh && ./install-rust.sh -y &&  rm install-rust.sh

RUN update-alternatives --set python3 /usr/bin/python3.9

# Create a new user and set the password
RUN useradd -m build && \
    echo "build:passwd" | chpasswd

RUN echo "%build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

#USER build
#WORKDIR /home/build

#RUN mkdir dev 
#WORKDIR dev
#RUN git clone https://github.com/pgedge/cli
#WORKDIR /home/build
#RUN python3 -m venv venv
#RUN source ~/venv/bin/activate
#RUN pip3 install --user --upgrade --no-warn-script-location pip

#USER root
#COPY ./config /tmp/.
#RUN chown build:build /tmp/config

#USER build
#WORKDIR /home/build/dev/cli/devel/setup
#RUN  ./1b-bashrc.sh
#RUN source /home/build/.bashrc
#RUN ./1c-awscli.sh
#RUN cp /tmp/config /home/build/.aws/. && chmod 600 /home/build/.aws/config && rm /tmp/config

#WORKDIR /home/build/dev/cli
#RUN pip3 install -r requirements.txt

#EXPOSE 22
#CMD ["/usr/sbin/init", "-D"]
#CMD ["/usr/sbin/sshd", "-D"]


# see https://hub.docker.com/_/rockylinux
# RockyLinux:9 missing /usr/sbin/init -> ../lib/systemd/systemd
#  see https://github.com/rocky-linux/sig-cloud-instance-images/issues/39
#RUN [ ! -f /usr/sbin/init ] && sudo dnf -y install systemd;
#ENV container=docker
#STOPSIGNAL SIGRTMIN+3
#VOLUME [ "/tmp", "/run", "/run/lock", "/run/systemd/container" ]
#WORKDIR /
#RUN ([ -d /lib/systemd/system/sysinit.target.wants ] && cd /lib/systemd/system/sysinit.target.wants/ && for i in *; do [ $i == \
#     systemd-tmpfiles-setup.service ] || rm -f $i; done); \
#rm -f /lib/systemd/system/multi-user.target.wants/*;\
#rm -f /etc/systemd/system/*.wants/*;\
#rm -f /lib/systemd/system/local-fs.target.wants/*; \
#rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
#rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
#rm -f /lib/systemd/system/basic.target.wants/*;\
#rm -f /lib/systemd/system/anaconda.target.wants/*;

#VOLUME [ "/sys/fs/cgroup" ]
#VOLUME ["/sys/fs/cgroup/systemd"]
#CMD ["/usr/sbin/init"]


#   yum-config-manager --enable rhel-8-for-x86_64-supplementary-rpms && \
#   yum-config-manager --enable codeready-builder-for-rhel-8-x86_64-rpms && \
