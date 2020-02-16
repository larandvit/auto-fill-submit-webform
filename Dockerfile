FROM local/c7-systemd

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