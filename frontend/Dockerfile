# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_grafana .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name grafana_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro  sarjitsu_grafana
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

# install grafana
RUN dnf -y install initscripts fontconfig
# needed for psycopg2 postgres library
RUN dnf -y install python3-pip postgresql-devel gcc redhat-rpm-config python3-devel
RUN rpm -Uvh https://grafanarel.s3.amazonaws.com/builds/grafana-2.5.0-pre1.x86_64.rpm
COPY conf/requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

ADD scripts/ /scripts
ADD api_server/ /opt/api_server

COPY conf/metadata_creation.service /lib/systemd/system/metadata_creation.service
COPY conf/api_engine.service /lib/systemd/system/api_engine.service
COPY conf/sar-index.cfg /etc/sar-index.cfg

# expose ports for grafana and api server
EXPOSE 3000 5000

RUN systemctl enable grafana-server metadata_creation
RUN systemctl enable api_engine

CMD ["/usr/sbin/init"]
