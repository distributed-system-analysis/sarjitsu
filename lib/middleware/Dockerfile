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

COPY conf/sar-index.cfg.example /etc/sar-index.cfg

COPY conf/metadata_creation.service /usr/lib/systemd/system/metadata_creation.service
COPY conf/api_engine.service /usr/lib/systemd/system/api_engine.service

ARG ES_HOST
ENV ES_HOST=${ES_HOST}
ARG ES_PORT
ENV ES_PORT=${ES_PORT}
ARG ES_PROTOCOL
ENV ES_PROTOCOL=${ES_PROTOCOL}
ARG INDEX_PREFIX
ENV INDEX_PREFIX=${INDEX_PREFIX}
ARG BULK_ACTION_COUNT
ENV BULK_ACTION_COUNT=${BULK_ACTION_COUNT}
ARG INDEX_VERSION
ENV INDEX_VERSION=${INDEX_VERSION}
ARG SHARD_COUNT
ENV SHARD_COUNT=${SHARD_COUNT}
ARG REPLICAS_COUNT
ENV REPLICAS_COUNT=${REPLICAS_COUNT}
ARG GRAFANA_DS_NAME
ENV GRAFANA_DS_NAME=${GRAFANA_DS_NAME}
ARG GRAFANA_DS_PATTERN
ENV GRAFANA_DS_PATTERN=${GRAFANA_DS_PATTERN}
ARG GRAFANA_TIMEFIELD
ENV GRAFANA_TIMEFIELD=${GRAFANA_TIMEFIELD}
ARG DB_HOST
ENV DB_HOST=${DB_HOST}
ARG DB_NAME
ENV DB_NAME=${DB_NAME}
ARG DB_USER
ENV DB_USER=${DB_USER}
ARG DB_PASSWORD
ENV DB_PASSWORD=${DB_PASSWORD}
ARG DB_PORT
ENV DB_PORT=${DB_PORT}
ARG MIDDLEWARE_PORT
ENV MIDDLEWARE_PORT=${MIDDLEWARE_PORT}

# expose ports for api server
# EXPOSE $MIDDLEWARE_PORT}
EXPOSE ${MIDDLEWARE_PORT}

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# CMD ["middleware"]

# RUN systemctl enable metadata_creation
# RUN systemctl enable api_engine
# CMD ["/usr/sbin/init"]
CMD ["api_engine"]
