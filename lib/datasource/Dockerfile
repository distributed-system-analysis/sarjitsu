# DEPLOYMENT INSTRUCTIONS
# To build the image, refer:
# docker build -t sarjitsu_elasticsearch .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name elastic_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

RUN dnf -y install java-1.8.0-openjdk initscripts

RUN rpm -Uvh https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.3.noarch.rpm
#	RUN /usr/share/elasticsearch/bin/plugin install mobz/elasticsearch-head

RUN sed -i "s/# network.host:.*/network.host: 0.0.0.0/g" \
    	   /etc/elasticsearch/elasticsearch.yml  && \
	   sed -i "s/#cluster.name: elasticsearch/cluster.name: elasticsearch20189/g" \
	   /etc/elasticsearch/elasticsearch.yml

RUN systemctl enable elasticsearch
EXPOSE 9200

CMD ["/usr/sbin/init"]
