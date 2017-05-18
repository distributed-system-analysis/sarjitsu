# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_backend --build-arg BACKEND_SERVER_PORT=80 .

# To run using the container, refer the following command:
# docker run --privileged -it -d \
#             --name node_jitsu \
#             -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
#             sarjitsu_backend

# optionally, supply -p 9210:80 to map the backend
# container's port 80 to your host at 9210
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

# deps
RUN dnf -y install net-tools procps git tar bzip2 redis python3-devel gcc nss_wrapper gettext
# nginx

# scaffolding
RUN mkdir -p /opt/sarjitsu/conf
ADD src/ /opt/sarjitsu/src
RUN cd /opt/sarjitsu/src && pip3 install -r requirements.txt

# copy configs from example files and modify them later through entrypoint
COPY conf/sarjitsu.ini.example /opt/sarjitsu/conf/sarjitsu.ini
COPY conf/sar-index.cfg.example /opt/sarjitsu/conf/sar-index.cfg
# COPY conf/sarjitsu_nginx.conf.example /etc/nginx/conf.d/sarjitsu_nginx.conf

ENV VOS_CONFIG_PATH=/opt/sarjitsu/conf/sar-index.cfg

ARG ES_HOST
ENV ES_HOST=${ES_HOST}
ARG ES_PORT
ENV ES_PORT=${ES_PORT}
ARG INDEX_PREFIX
ENV INDEX_PREFIX=${INDEX_PREFIX}
ARG INDEX_VERSION
ENV INDEX_VERSION=${INDEX_VERSION}
ARG BULK_ACTION_COUNT
ENV BULK_ACTION_COUNT=${BULK_ACTION_COUNT}
ARG SHARD_COUNT
ENV SHARD_COUNT=${SHARD_COUNT}
ARG REPLICAS_COUNT
ENV REPLICAS_COUNT=${REPLICAS_COUNT}
ARG GRAFANA_HOST
ENV GRAFANA_HOST=${GRAFANA_HOST}
ARG GRAFANA_PORT
ENV GRAFANA_PORT=${GRAFANA_PORT}
ARG MIDDLEWARE_HOST
ENV MIDDLEWARE_HOST=${MIDDLEWARE_HOST}
ARG MIDDLEWARE_PORT
ENV MIDDLEWARE_PORT=${MIDDLEWARE_PORT}
ARG MIDDLEWARE_ENDPOINT
ENV MIDDLEWARE_ENDPOINT=${MIDDLEWARE_ENDPOINT}

# RUN sed -i -r s#^.*listen.*\ 80.*##g /etc/nginx/nginx.conf
RUN touch /opt/sarjitsu/src/flaskapp.sock
# RUN chmod 710 /opt/sarjitsu/{src,conf} && chown -R nginx:nginx /opt/sarjitsu
# RUN usermod -a -G root nginx

WORKDIR /opt/sarjitsu/src

# VOLUME /var/lib/postgresql/data

# expose ports for sarjitsu
ARG BACKEND_SERVER_PORT
EXPOSE ${BACKEND_SERVER_PORT}

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# ENTRYPOINT /docker-entrypoint.sh && /usr/sbin/init

CMD ["backend"]
