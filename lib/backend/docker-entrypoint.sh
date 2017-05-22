#!/bin/bash

set -e

log(){
    echo -e "[$(date +'%D %H:%M:%S %Z')] - $*"
}

# Add as command if needed
if [ "${1:0:1}" = '-' ]; then
    set -- backend "$@"
fi

update_configs(){
  # whoami
    # ls -lh /home/flask
    # cp /opt/sarjitsu/conf/sar-index.cfg /home/flask/sar-index.cfg.tmp

    if [[ ! -z $ES_HOST ]]; then
	sed -i -r 's#^host\s?=.*#host = '$ES_HOST'#g' /opt/sarjitsu/conf/sar-index.cfg
    else
	sed -i -r 's#^host\s?=.*#host = datasource#g' /opt/sarjitsu/conf/sar-index.cfg
    fi
    sed -i -r 's#^port\s?=.*#port = '$ES_PORT'#g' /opt/sarjitsu/conf/sar-index.cfg

    sed -i -r 's#^index_prefix\s?=.*#index_prefix = '$INDEX_PREFIX'#g' /opt/sarjitsu/conf/sar-index.cfg
    sed -i -r 's#^index_version\s?=.*#index_version = '$INDEX_VERSION'#g' /opt/sarjitsu/conf/sar-index.cfg
    sed -i -r 's#^bulk_action_count\s?=.*#bulk_action_count = '$BULK_ACTION_COUNT'#g' /opt/sarjitsu/conf/sar-index.cfg
    sed -i -r 's#^number_of_shards\s?=.*#number_of_shards = '$SHARD_COUNT'#g' /opt/sarjitsu/conf/sar-index.cfg
    sed -i -r 's#^number_of_replicas\s?=.*#number_of_replicas = '$REPLICAS_COUNT'#g' /opt/sarjitsu/conf/sar-index.cfg

    if [[ ! -z $GRAFANA_HOST ]]; then
	sed -i -r 's#^dashboard_url\s?=.*#dashboard_url = http://'$GRAFANA_HOST':'$GRAFANA_PORT'/#g' /opt/sarjitsu/conf/sar-index.cfg
    fi

    sed -i -r 's#^api_url\s?=.*#api_url = http://'$MIDDLEWARE_HOST:$MIDDLEWARE_PORT$MIDDLEWARE_ENDPOINT'#g' /opt/sarjitsu/conf/sar-index.cfg

    # cp /home/flask/sar-index.cfg.tmp /opt/sarjitsu/conf/sar-index.cfg
}

if [ "$1" = 'backend' ]; then
  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)
  envsubst < /passwd.template > /tmp/passwd
  export LD_PRELOAD=/usr/lib64/libnss_wrapper.so
  export NSS_WRAPPER_PASSWD=/tmp/passwd
  export NSS_WRAPPER_GROUP=/etc/group

  echo $(id)

  update_configs
  cd /opt/sarjitsu/src/
  /usr/bin/uwsgi --ini /opt/sarjitsu/conf/sarjitsu.ini
fi

exec "$@"
