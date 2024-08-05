FROM rockylinux:8

RUN dnf -y install sudo python39 python39-devel python39-pip
RUN dnf -y install git wget sqlite vim

RUN useradd build


USER build
WORKDIR /home/build
RUN mkdir dev 
WORKDIR dev
RUN git clone https://github.com/pgedge/cli
WORKDIR cli/devel/setup
RUN ./1a-toolset.sh


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

VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

