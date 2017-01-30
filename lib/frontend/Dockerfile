# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_grafana .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name grafana_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro  sarjitsu_grafana
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

# install grafana
RUN dnf -y install initscripts fontconfig python3-pip
RUN pip3 install configparser

# needed for psycopg2 postgres library
RUN rpm -Uvh https://grafanarel.s3.amazonaws.com/builds/grafana-3.0.1-1.x86_64.rpm

COPY conf/grafana.ini.example /etc/grafana/grafana.ini

RUN chown -R root:grafana /etc/grafana/grafana.ini
# RUN iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 3000

ARG GRAFANA_DB_TYPE
ENV GRAFANA_DB_TYPE=${GRAFANA_DB_TYPE}
ARG DB_HOST
ENV DB_HOST=${DB_HOST}
ARG DB_PORT
ENV DB_PORT=${DB_PORT}
ARG DB_NAME
ENV DB_NAME=${DB_NAME}
ARG DB_USER
ENV DB_USER=${DB_USER}
ARG DB_PASSWORD
ENV DB_PASSWORD=${DB_PASSWORD}

# expose ports for grafana
ARG GRAFANA_PORT
EXPOSE ${GRAFANA_PORT}

COPY update_grafana_conf.py /
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

RUN systemctl enable grafana-server
CMD ["/usr/sbin/init"]
