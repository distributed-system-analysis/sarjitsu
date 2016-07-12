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
            echo "Usage: $0 [ options ]"
            echo "Options are:"
            echo -e "\t[-r deploy fresh instances of all containers. Default 0 (1 is for fresh)]"
            echo -e "\tNote that [-r 1] would override all IP addresses provided in config file\n"
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
    CLEAN_IDS=($MIDDLEWARE_CONTAINER_ID $BACKEND_CONTAINER_ID)
    CONFIGURABLES=($METRICSTORE_CONTAINER_ID $DATASOURCE_CONTAINER_ID $FRONTEND_CONTAINER_ID)
    
    declare -A components
    components+=( [$METRICSTORE_CONTAINER_ID]="DB_HOST" \
					     [$DATASOURCE_CONTAINER_ID]="ES_HOST" \
					     [$FRONTEND_CONTAINER_ID]="GRAFANA_HOST" \
					     [$MIDDLEWARE_CONTAINER_ID]="MIDDLEWARE_HOST" \
					     [$BACKEND_CONTAINER_ID]="BACKEND_HOST" )    

    sed -i -r 's#^MIDDLEWARE_HOST=.*#MIDDLEWARE_HOST=#g' $APP_CONF
    export MIDDLEWARE_HOST=''
    
    if [ $1 -eq 0 ]; then
	for host_type in "${CONFIGURABLES[@]}"; do
	    host_value=$(eval "echo \$${components[${host_type}]}")
	    if [[ -z $host_value ]]; then
		CLEAN_IDS+=($host_type)
	    fi
	done
    else
	for host_type in "${CONFIGURABLES[@]}"; do
	    CLEAN_IDS+=($host_type)
	done
    fi	

    GREP_PATTERNS=''
    for host_type in "${CLEAN_IDS[@]}"; do
	GREP_PATTERNS+=" -e $host_type"
    done
    
    SCHEDULED_CLEANUPS=$(docker ps -a | grep $GREP_PATTERNS | awk -F' ' '{print $1}')
    
    #CLEAN_IDS=$(docker ps -a | grep -P '^.*(\ssarjitsu.*|'$METRICSTORE_CONTAINER_ID')$' | awk -F' ' '{print $1}')
    if [[ ! -z $SCHEDULED_CLEANUPS ]]; then
	log "cleaning up previously created sarjitsu instances for: [${CLEAN_IDS[@]}]"
	#docker stop $SCHEDULED_CLEANUPS
	docker rm -f $SCHEDULED_CLEANUPS
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

check_host_status(){
  CHECK_HOST=$(ping -c 1 $1 | grep "1 received")
  if [[ -z $CHECK_HOST ]]; then
    log "$2 is down."
    log "Check your *_HOST endpoint in conf/sarjitsu.conf, if running custom installation"
    log "Else run with '$ ./setup.sh -r 1' to do a fresh installation."
    log "CAUTION: Above recommendation would result in removal of old conf/sarjitsu.conf"
    exit 1
  fi
}

main(){
  log "building and running sarjitsu now"
  if [[ -z $DB_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/metricstore/
    echo -e 'Progress: ##                   (10%)\r'
    ./launch_postgres $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $METRICSTORE_CONTAINER_ID"
      exit -1
    fi
    echo -e 'Progress: ####                 (20%)\r'
    DB_HOST=`get_container_IP $METRICSTORE_CONTAINER_ID`
    update_sarjitsu_config DB_HOST $DB_HOST
  else
    check_host_status $DB_HOST "postgreSQL host"
  fi

  if [[ -z $ES_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/datasource/
    echo -e 'Progress: #####                (25%)\r'
    ./launch_elastic $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $DATASOURCE_CONTAINER_ID"
      exit -1
    fi
    echo -e 'Progress: ######               (35%)\r'
    ES_HOST=`get_container_IP $DATASOURCE_CONTAINER_ID`
    update_sarjitsu_config ES_HOST $ES_HOST

    update_es_config host $ES_HOST
    update_es_config port $ES_PORT

    log "Attempting to create Index template in Elasticsearch"
    log "This might take 5-10 multiple attempts.."
    while :; do
    	status=`curl -s $ES_PROTOCOL://$ES_HOST:$ES_PORT/_cluster/health | egrep "yellow|green"`
    	if [[ ! -z $status ]]; then
    	    ${ROOT_DIR%/}/utils/es-create-sarjitsu-templates $ES_CONF $SAR_MAPPING_PATH
    	    if [ ! $? -eq 0 ]; then
        		log "index template creation for sarjitsu failed."
            exit -1
    	    fi
          echo -e 'Progress: ########             (40%)\r'
    	    break
    	else
    	    log "unable to contact Elasticsearch; sleeping for 2 secs"
    	    sleep 2
    	fi
    done
  else
    check_host_status $ES_HOST "Elasticsearch host"
  fi

  if [[ -z $GRAFANA_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/frontend/
    ./launch_grafana $APP_CONF
    echo -e 'Progress: ##########           (50%)\r'
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $FRONTEND_CONTAINER_ID"
      exit -1
    fi
    echo -e 'Progress: ############         (60%)\r'
    GRAFANA_HOST=`get_container_IP $FRONTEND_CONTAINER_ID`
    update_sarjitsu_config GRAFANA_HOST $GRAFANA_HOST
  else
    check_host_status $GRAFANA_HOST "Grafana host"
  fi

  if [[ -z $MIDDLEWARE_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/middleware/
    echo -e 'Progress: #############        (65%)\r'
    ./launch_api_server $APP_CONF
    if [[ ! $? -eq 0 ]]; then
      log "unable to run container: $MIDDLEWARE_CONTAINER_ID"
      exit -1
    fi
    echo -e 'Progress: ##############       (70%)\r'
    MIDDLEWARE_HOST=`get_container_IP $MIDDLEWARE_CONTAINER_ID`
    update_sarjitsu_config MIDDLEWARE_HOST $MIDDLEWARE_HOST
  else
    check_host_status $MIDDLEWARE_HOST "Middleware host"
  fi

  cd ${ROOT_DIR%/}/lib/backend/
  echo -e 'Progress: ###############      (75%)\r'
  ./launch_backend $APP_CONF
  if [[ ! $? -eq 0 ]]; then
    log "unable to run container: $BACKEND_CONTAINER_ID"
    exit -1
  fi
  echo -e 'Progress: #################    (85%)\r'
  BACKEND_HOST=`get_container_IP $BACKEND_CONTAINER_ID`
  update_sarjitsu_config BACKEND_HOST $BACKEND_HOST
  echo -e 'Progress: #################### (100%)\r\n'
  log "Done! Go to http://$BACKEND_HOST:$BACKEND_SERVER_PORT/ to access your application"
  log "Note: The same address is mapped to http://127.0.0.1:$BACKEND_PORT_MAPPING"
  log "Recommendation: Map this to an reverse proxy provider, such as Nginx"
}

bootstrap(){
  if [ $FRESH -eq 1 ]; then
      log "(FRESH INSTALL) overriding default IP addresses under sarjitsu.conf"
      log "NOTE: This would remove all sarjitsu containerized components."
    cleanup_host_info
    cp $ES_CONF.example $ES_CONF
    cp $APP_CONF.example $APP_CONF
    cleanup_opt=1
  else
    log "(CUSTOM INSTALL) CONFIGURABLES: any/all of (Elastic, Grafana and Postgres)"
    log "(CUSTOM INSTALL) reusing IPs allotted to \$CONFIGURABLES under sarjitsu.conf"
    log "NOTE: This would pole for containers already up & running, and relaunch missing pieces."
    cleanup_opt=0
  fi
  source $APP_CONF
  cleanup_containers $cleanup_opt
  main
}

status=`docker --version 2> /dev/null`
if [ ! $? -eq 0 ]; then
  log "You don't have docker installed."
  log "Run this again after installing docker"
  log "Refer to INSTALLATION section of README for more"
  exit -1
fi

status=`python3 -c 'import elasticsearch' 2> /dev/null`
if [ ! $? -eq 0 ]; then
  log "You don't have python3-elasticsearch installed."
  log "Install it through 'pip3 install -r requirements.txt'"
  log "Refer to INSTALLATION section of README for more"
  exit -1
fi

status=`python3 -c 'import prettytable' 2> /dev/null`
if [ ! $? -eq 0 ]; then
  log "You don't have python3-PTable installed, needed by cmdline tool 'vizit'."
  log "Install it through 'pip3 install -r requirements.txt'"
  log "Refer to INSTALLATION section of README for more"
  exit -1
fi

bootstrap
