# DEPLOYMENT INSTRUCTIONS
# To build the image, refer:
# docker build -t sarjitsu_elasticsearch .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name elastic_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

RUN dnf -y install java-1.8.0-openjdk initscripts

# # ensure elasticsearch user exists
# RUN addgroup -S elasticsearch && adduser -S -G elasticsearch elasticsearch

RUN rpm -Uvh https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.3.noarch.rpm
RUN /usr/share/elasticsearch/bin/plugin install mobz/elasticsearch-head

ENV PATH /usr/share/elasticsearch/bin:$PATH

# VOLUME /usr/share/elasticsearch/data

# ENV es_port=${es_port}
ARG ES_PORT
EXPOSE ${ES_PORT}

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

RUN chmod -R 777 /usr/share/elasticsearch/
RUN chmod -R 777 /etc/elasticsearch/
USER nobody

# following illustrates different appraoches to running elasticsearch
# for now, we're gonna use non privileged mode
CMD ["elasticsearch"]

# RUN systemctl enable elasticsearch
# CMD ["/usr/sbin/init"]
