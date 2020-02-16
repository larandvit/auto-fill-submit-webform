FROM centos:7

ENV container docker

RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

VOLUME [ "/sys/fs/cgroup" ]

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm && yum clean all

RUN yum install -y python3 python3-pip && yum clean all

RUN yum install -y cronie && yum clean all

RUN pip3.6 install requests

RUN rm -rf /etc/localtime
RUN ln -s /usr/share/zoneinfo/America/Toronto /etc/localtime

RUN crontab -l | { cat; echo "25 04 * * sun,mon,tue python3 /app/submit_webform.py -f /app/data_parking.json"; } | crontab -

RUN mkdir /app

WORKDIR /app

COPY submit_webform.py .
COPY data_parking.json .

CMD ["/usr/sbin/init"]