FROM centos:7.7.1908

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm

RUN yum install -y python3 python3-pip

RUN yum install -y cronie

RUN pip3.6 install requests

RUN crontab -l | { cat; echo "30 15 * * sat,mon,tue python3 /app/submit_webform.py -f /app/data_parking.json"; } | crontab -

RUN mkdir /app

WORKDIR /app

COPY submit_webform.py .
COPY data_parking.json .

CMD tail -f /dev/null