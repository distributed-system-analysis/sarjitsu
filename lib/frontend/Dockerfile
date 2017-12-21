# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_grafana .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name grafana_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro  sarjitsu_grafana
###########################################################

FROM fedora:25
MAINTAINER arcolife <archit.py@gmail.com>

# install grafana
RUN dnf -y install initscripts fontconfig python3-pip nss_wrapper gettext urw-fonts
RUN pip3 install configparser

# needed for psycopg2 postgres library
RUN rpm -Uvh https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.6.3-1.x86_64.rpm

COPY conf/grafana.ini.example /etc/grafana/grafana.ini

# RUN chown -R grafana:grafana /etc/grafana/grafana.ini
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

# RUN useradd -ms /bin/bash grafana

RUN chgrp -R 0 /etc/grafana/ /update_grafana_conf.py /usr/share/grafana/ /var/lib/grafana /var/log/grafana\
  && chmod -R g+rwX /etc/grafana/ /update_grafana_conf.py /usr/share/grafana/ /var/lib/grafana /var/log/grafana\
  && chown -R grafana:root /etc/grafana/ /update_grafana_conf.py /usr/share/grafana /var/lib/grafana /var/log/grafana/

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

USER grafana

CMD ["grafana-server"]
