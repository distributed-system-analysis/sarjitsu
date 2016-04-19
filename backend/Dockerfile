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

# install npm, grunt-cli and other utils
RUN dnf -y install npm net-tools procps git tar wget bzip2
RUN npm install -g grunt-cli forever

ADD src/ /src
RUN cd /src && npm install && pip3 install -r requirements.txt

COPY conf/sarjitsu.service /lib/systemd/system/sarjitsu.service
COPY conf/sar-index.cfg /etc/sar-index.cfg
ENV VOS_CONFIG_PATH=/etc/sar-index.cfg

COPY conf/nodeup /src/nodeup

# expose ports for sarjitsu
EXPOSE 80

RUN systemctl enable sarjitsu
WORKDIR /src

CMD ["/usr/sbin/init"]
