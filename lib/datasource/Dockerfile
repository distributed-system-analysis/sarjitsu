# DEPLOYMENT INSTRUCTIONS
# To build the image, refer:
# docker build -t sarjitsu_elasticsearch .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name elastic_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
###########################################################

FROM fedora:25
MAINTAINER arcolife <archit.py@gmail.com>

RUN dnf -y install procps net-tools java-1.8.0-openjdk initscripts

# # ensure elasticsearch user exists
# RUN addgroup -S elasticsearch && adduser -S -G elasticsearch elasticsearch

RUN rpm -Uvh https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.1.1.rpm
# RUN /usr/share/elasticsearch/bin/plugin install mobz/elasticsearch-head

RUN dnf -y install nss_wrapper gettext

ENV PATH /usr/share/elasticsearch/bin:$PATH

COPY conf/passwd.template /${HOME}/passwd.template
# VOLUME /usr/share/elasticsearch/data

# ENV es_port=${es_port}
ARG ES_PORT
EXPOSE ${ES_PORT}

RUN chgrp -R 0 /usr/share/elasticsearch /etc/elasticsearch /var/{run,lib,log}/elasticsearch \
  && chmod -R g+rwX /usr/share/elasticsearch /etc/elasticsearch /var/{run,lib,log}/elasticsearch \
  && chown -R elasticsearch:root /usr/share/elasticsearch /etc/elasticsearch /var/{run,lib,log}/elasticsearch

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

USER elasticsearch

CMD ["elastic"]
