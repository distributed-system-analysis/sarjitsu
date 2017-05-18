#!/bin/bash

set -e

# Add elasticsearch as command if needed
if [ "${1:0:1}" = '-' ]; then
    set -- elasticsearch "$@"
fi

sed -i "s/# network.host:.*/network.host: 0.0.0.0/g" \
    /etc/elasticsearch/elasticsearch.yml

# sed -i -r 's#elasticsearch\$RANDOM#'$ES_CLUSTER_NAME'#g' /etc/elasticsearch/elasticsearch.yml
sed -i -r "s/#cluster.name: elasticsearch/cluster.name: elasticsearch$RANDOM/g" \
    /etc/elasticsearch/elasticsearch.yml

# Drop root privileges if we are running elasticsearch
# allow the container to be started with `--user`

# if [ "$1" = 'elasticsearch' ]; then
if [ "$1" = 'elasticsearch' -a "$(id -u)" = '0' ]; then
    # Change the ownership of user-mutable directories to elasticsearch
    # for path in \
	# 	/usr/share/elasticsearch/data \
	# 	/usr/share/elasticsearch/logs \
	# ; do
    # 	chown -R elasticsearch:elasticsearch "$path"
    # done
    echo "through PATH"
    ES_HOME=/usr/share/elasticsearch
    CONF_DIR=/etc/elasticsearch
    CONF_FILE=/etc/elasticsearch/elasticsearch.yml
    DATA_DIR=/var/lib/elasticsearch
    LOG_DIR=/var/log/elasticsearch
    PID_DIR=/var/run/elasticsearch

    chown -R elasticsearch:elasticsearch /var/{run,lib,log}/elasticsearch /etc/elasticsearch
    
    set -- elasticsearch \
        -Des.pidfile=$PID_DIR/elasticsearch.pid \
        -Des.default.path.home=$ES_HOME \
        -Des.default.path.logs=$LOG_DIR \
        -Des.default.path.data=$DATA_DIR \
        -Des.default.config=$CONF_FILE \
        -Des.default.path.conf=$CONF_DIR
    # exec su-exec elasticsearch "$BASH_SOURCE" "$@"
else
    echo "through SYSTEMD / init"
fi

# As argument is not related to elasticsearch,
# then assume that user wants to run his own process,
# for example a `bash` shell to explore this image
exec "$@"
