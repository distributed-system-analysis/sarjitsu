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
RUN rpm -Uvh https://grafanarel.s3.amazonaws.com/builds/grafana-3.0.1-1.x86_64.rpm
COPY conf/grafana.ini /etc/grafana/grafana.ini

RUN chown -R root:grafana /etc/grafana/grafana.ini
# RUN iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 3000

# expose ports for grafana
EXPOSE 3000

RUN systemctl enable grafana-server

CMD ["/usr/sbin/init"]
