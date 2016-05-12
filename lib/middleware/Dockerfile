# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_api .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name api_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro  sarjitsu_api
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

RUN dnf -y install initscripts
# needed for psycopg2 postgres library
RUN dnf -y install python3-pip postgresql-devel gcc redhat-rpm-config python3-devel
COPY conf/requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

ADD scripts/ /scripts
ADD api_server/ /opt/api_server

COPY conf/metadata_creation.service /usr/lib/systemd/system/metadata_creation.service
COPY conf/api_engine.service /usr/lib/systemd/system/api_engine.service
COPY conf/sar-index.cfg /etc/sar-index.cfg

# expose ports for api server
EXPOSE 80

RUN systemctl enable metadata_creation
RUN systemctl enable api_engine

CMD ["/usr/sbin/init"]
