FROM rockylinux:8

RUN dnf -y update && dnf -y install sudo python39 python39-devel python39-pip

RUN dnf -y install sudo openssh-server systemd && \
    dnf -y install dnf-plugins-core && dnf config-manager --set-enabled powertools && \
    dnf -y install net-tools wget curl pigz sqlite which zip gcc-toolset-13

RUN dnf -y install perl-devel perl-CPAN perl-JSON perl-App-cpanminus && \
    dnf -y install cpan
#RUN echo yes | sudo cpan FindBin
#RUN dnf -y install  sudo cpan IPC::Run

RUN dnf -y install epel-release && dnf -y groupinstall 'development tools' && \
    dnf -y --nobest install zlib-devel bzip2-devel lbzip2 \
      openssl-devel libxslt-devel libevent-devel c-ares-devel \
      perl-ExtUtils-Embed pam-devel openldap-devel boost-devel chrpath clang-devel \
      llvm-devel cmake libxml2-devel libedit-devel sqlite-devel \
      *ossp-uuid* openjpeg2-devel libyaml libyaml-devel \
      ncurses-compat-libs systemd-devel unixODBC-devel protobuf-c-devel libyaml-devel \
      lz4-devel libzstd-devel krb5-devel geos-devel proj-devel gdal sqlite-devel \
      podman podman-compose @ruby:3.0 ruby-devel rpm-build squashfs-tools && \
    gem install fpm

RUN dnf -y install java-17-openjdk && yum clean all && rm -rf /var/cache/yum

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > install-rust.sh 
RUN chmod 755 install-rust.sh && ./install-rust.sh -y &&  rm install-rust.sh

RUN update-alternatives --set python3 /usr/bin/python3.9

RUN useradd build
RUN echo "%build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER build
WORKDIR /home/build
RUN mkdir dev 
WORKDIR dev
RUN git clone https://github.com/pgedge/cli
WORKDIR /home/build
RUN python3 -m venv venv
RUN source ~/venv/bin/activate
RUN pip3 install --upgrade --no-warn-script-location pip



# see https://hub.docker.com/_/rockylinux
# RockyLinux:9 missing /usr/sbin/init -> ../lib/systemd/systemd
#  see https://github.com/rocky-linux/sig-cloud-instance-images/issues/39
#RUN [ ! -f /usr/sbin/init ] && sudo dnf -y install systemd;
#RUN ([ -d /lib/systemd/system/sysinit.target.wants ] && cd /lib/systemd/system/sysinit.target.wants/ && for i in *; do [ $i == \
#systemd-tmpfiles-setup.service ] || rm -f $i; done); \
#rm -f /lib/systemd/system/multi-user.target.wants/*;\
#rm -f /etc/systemd/system/*.wants/*;\
#rm -f /lib/systemd/system/local-fs.target.wants/*; \
#rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
#rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
#rm -f /lib/systemd/system/basic.target.wants/*;\
#rm -f /lib/systemd/system/anaconda.target.wants/*;

#VOLUME [ "/sys/fs/cgroup" ]
#CMD ["/usr/sbin/init"]

