# DEPLOYMENT INSTRUCTIONS

# To build the image, refer:
# docker build -t sarjitsu_backend .

# To run using the container, refer the following command:
# docker run --privileged -it -d --name node_jitsu -v /sys/fs/cgroup:/sys/fs/cgroup:ro  sarjitsu_backend

# optionally, supply -p 9210:80 to map the backend
# container's port 80 to your host at 9210
###########################################################

FROM fedora:23
MAINTAINER arcolife <archit.py@gmail.com>

RUN dnf -y install net-tools procps git tar bzip2 redis python3-devel gcc nginx
RUN mkdir -p /opt/sarjitsu/conf
ADD src/ /opt/sarjitsu/src
RUN cd /opt/sarjitsu/src && pip3 install -r requirements.txt

COPY conf/sarjitsu.ini /opt/sarjitsu/conf/sarjitsu.ini
COPY conf/sar-index.cfg /opt/sarjitsu/conf/sar-index.cfg
COPY conf/sarjitsu.service /lib/systemd/system/sarjitsu.service
COPY conf/sarjitsu_nginx.conf /etc/nginx/conf.d/sarjitsu_nginx.conf

ENV VOS_CONFIG_PATH=/opt/sarjitsu/conf/sar-index.cfg

RUN sed -i -r s#^.*listen.*\ 80.*##g /etc/nginx/nginx.conf
RUN touch /opt/sarjitsu/src/flaskapp.sock
RUN chmod 710 /opt/sarjitsu/{src,conf} && chown -R nginx:nginx /opt/sarjitsu
RUN usermod -a -G root nginx

# expose ports for sarjitsu
EXPOSE 80

RUN systemctl enable redis nginx sarjitsu

WORKDIR /opt/sarjitsu/src

CMD ["/usr/sbin/init"]
