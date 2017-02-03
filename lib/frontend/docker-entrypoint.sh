#!/bin/bash

log(){
  echo -e "[$(date +'%D %H:%M:%S %Z')] - $*"
}

# Add as command if needed
if [ "${1:0:1}" = '-' ]; then
	set -- grafana-server "$@"
fi

if [ "$1" = 'grafana-server' -a "$(id -u)" = '0' ]; then

  if [[ -z $DB_HOST ]]; then
    DB_HOST='metricstore'
    log "DB_HOST set to default - 'metricstore'"
  fi

  while :; do
    curl -s http://$DB_HOST:$DB_PORT
    if [ $? -eq 52 ]; then
      set -e
      python3 /update_grafana_conf.py
      log "updated grafana credentials in /etc/grafana/grafana.ini"

      # 52 is empty reply from server, meaning db is up
      # this is to counter "getsockopt: connection refused to postgres"
      # ref: https://github.com/distributed-system-analysis/sarjitsu/issues/34
      log "connection etablished - [postgres]"

      cd /usr/share/grafana/
      source /etc/sysconfig/grafana-server
      set -- grafana-server \
                  --config=${CONF_FILE} \
                  --pidfile=${PID_FILE} \
                  cfg:default.paths.logs=${LOG_DIR} \
                  cfg:default.paths.data=${DATA_DIR} \
                  cfg:default.paths.plugins=${PLUGINS_DIR}
      break
    else
        log "unable to contact $DB_HOST; retrying after 1 second."
        sleep 1
    fi
  done
fi

exec "$@"
