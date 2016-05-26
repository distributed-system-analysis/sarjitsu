#!/bin/bash

log(){
  echo -e "[$(date +'%D %H:%M:%S %Z')] - $*"
}

user_interrupt(){
  log "\nKeyboard Interrupt detected."
  exit 1
}

trap user_interrupt SIGINT

ROOT_DIR=`echo $PWD`

ES_CONF=${ROOT_DIR%/}/conf/es.cfg
APP_CONF=${ROOT_DIR%/}/conf/sarjitsu.conf
SAR_MAPPING_PATH=${ROOT_DIR%/}/utils/mappings/

if [ ! -f $ES_CONF ]; then
  log "generated $ES_CONF"
  cp $ES_CONF.example $ES_CONF
fi

if [ ! -f $APP_CONF ]; then
  log "generated $APP_CONF"
  cp $APP_CONF.example $APP_CONF
fi

while getopts "h?r:" opt; do
    case "$opt" in
        h|\?)
            echo "Usage: # $0 [OPTIONS]"
            echo "[-r deploy fresh instances of all containers. Default 0] [0/1]"
            echo -e "\t -r=1 would override all IP addresses provided in config file"
            exit 0
            ;;
        r)  FRESH=$OPTARG
            ;;
    esac
done

if [[ -z $FRESH ]]; then
  FRESH=0
fi

cleanup_containers(){
  CLEAN_IDS=$(docker ps -a | grep -P '^.*(\ssarjitsu.*|'$METRICSTORE_CONTAINER_ID')$' | awk -F' ' '{print $1}')
  if [[ ! -z $CLEAN_IDS ]]; then
    log "cleaning up previously created sarjitsu instances"
    docker stop $CLEAN_IDS
    docker rm $CLEAN_IDS
  fi
}

cleanup_host_info(){
  for host_type in DB_HOST ES_HOST GRAFANA_HOST MIDDLEWARE_HOST; do
    sed -i -r 's#^'$host_type'=.*#'$host_type'=#g' $APP_CONF
  done
}

update_es_config(){
  sed -i -r 's#^'$1'\s?=.*#'$1' = '$2'#g' $ES_CONF
}

update_sarjitsu_config(){
  # call this to update conf files, so that it could be used
  sed -i -r 's#^'$1'=.*#'$1'='$2'#g' $APP_CONF
}

get_container_IP(){
  echo `docker inspect $1 | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`
}

main(){
  log "building and running sarjitsu now"

  if [[ -z $DB_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/metricstore/
    ./launch_postgres $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $METRICSTORE_CONTAINER_ID"
      exit -1
    fi
    DB_HOST=`get_container_IP $METRICSTORE_CONTAINER_ID`
    update_sarjitsu_config DB_HOST $DB_HOST
  fi

  if [[ -z $ES_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/datasource/
    ./launch_elastic $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $DATASOURCE_CONTAINER_ID"
      exit -1
    fi
    ES_HOST=`get_container_IP $DATASOURCE_CONTAINER_ID`
    update_sarjitsu_config ES_HOST $ES_HOST

    update_es_config host $ES_HOST
    update_es_config port $ES_PORT

    while :; do
    	status=`curl -s $ES_PROTOCOL://$ES_HOST:$ES_PORT/_cluster/health | egrep "yellow|green"`
    	if [[ ! -z $status ]]; then
    	    ${ROOT_DIR%/}/utils/es-create-sarjitsu-templates $ES_CONF $SAR_MAPPING_PATH
    	    if [ ! $? -eq 0 ]; then
        		log "index template creation for sarjitsu failed."
            exit -1
    	    fi

    	    break
    	else
    	    log "unable to contact Elasticsearch; sleeping for 2 secs"
    	    sleep 2
    	fi
    done
  fi

  if [[ -z $GRAFANA_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/frontend/
    ./launch_grafana $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $FRONTEND_CONTAINER_ID"
      exit -1
    fi
    GRAFANA_HOST=`get_container_IP $FRONTEND_CONTAINER_ID`
    update_sarjitsu_config GRAFANA_HOST $GRAFANA_HOST
  fi

  if [[ -z $MIDDLEWARE_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/middleware/
    ./launch_api_server $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $MIDDLEWARE_CONTAINER_ID"
      exit -1
    fi
    MIDDLEWARE_HOST=`get_container_IP $MIDDLEWARE_CONTAINER_ID`
    update_sarjitsu_config MIDDLEWARE_HOST $MIDDLEWARE_HOST
  fi

  cd ${ROOT_DIR%/}/lib/backend/
  ./launch_backend $APP_CONF
  if [[ ! $? -eq 0 ]]; then
    log "unable to run container: $BACKEND_CONTAINER_ID"
    exit -1
  fi

  BACKEND_HOST=`get_container_IP $BACKEND_CONTAINER_ID`
  log "Done! Go to http://$BACKEND_HOST:$BACKEND_SERVER_PORT/ to access your application"
}

status=`docker --version`
if [ $? -eq 0 ]; then
  if [ $FRESH -eq 1 ]; then
    log "(FRESH INSTALL) overriding default IP addresses under sarjitsu.conf"
    cleanup_host_info
    cp $ES_CONF.example $ES_CONF
    cp $APP_CONF.example $APP_CONF
  else
    log "(CUSTOM INSTALL) using earlier set of IP addresses under sarjitsu.conf"
  fi
  source $APP_CONF
  cleanup_containers
  main
else
  log "You don't have docker installed."
  log "Run this again after installing docker"
fi
