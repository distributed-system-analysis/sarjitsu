#!/bin/bash

user_interrupt(){
  echo -e "\n\nKeyboard Interrupt detected."
  exit 1
}

trap user_interrupt SIGINT
trap user_interrupt SIGTSTP

source conf/sarjitsu.conf

ROOT_DIR=`echo $PWD`

update_host_configs(){
  # call this to update conf files, so that it could be used
  sed -i -r 's#^'$1'=.*#'$1'='$2'#g' ${ROOT_DIR%/}/conf/sarjitsu.conf
}

get_container_IP(){
  echo `docker inspect $1 | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`
}

main(){
  echo "building and running sarjitsu now"

  if [[ -z $DB_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/metricstore/
    ./launch_postgres
    if [[ ! $? -eq 0 ]]; then
      echo -e "\nunable to run container: $METRICSTORE_CONTAINER_ID"
      exit -1
    fi
    DB_HOST=`get_container_IP $METRICSTORE_CONTAINER_ID`
    update_host_configs DB_HOST $DB_HOST
  fi

  if [[ -z $ES_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/datasource/
    ./launch_elastic
    if [[ ! $? -eq 0 ]]; then
      echo -e "\nunable to run container: $DATASOURCE_CONTAINER_ID"
      exit -1
    fi
    ES_HOST=`get_container_IP $DATASOURCE_CONTAINER_ID`
    update_host_configs ES_HOST $ES_HOST
  fi

  if [[ -z $GRAFANA_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/frontend/
    ./launch_grafana
    if [[ ! $? -eq 0 ]]; then
      echo -e "\nunable to run container: $FRONTEND_CONTAINER_ID"
      exit -1
    fi
    GRAFANA_HOST=`get_container_IP $FRONTEND_CONTAINER_ID`
    update_host_configs GRAFANA_HOST $GRAFANA_HOST
  fi

  if [[ -z $MIDDLEWARE_HOST ]]; then
    cd ${ROOT_DIR%/}/lib/middleware/
    ./launch_api_server
    if [[ ! $? -eq 0 ]]; then
      echo -e "\nunable to run container: $MIDDLEWARE_CONTAINER_ID"
      exit -1
    fi
    MIDDLEWARE_HOST=`get_container_IP $MIDDLEWARE_CONTAINER_ID`
    update_host_configs MIDDLEWARE_HOST $MIDDLEWARE_HOST
  fi

  cd ${ROOT_DIR%/}/lib/backend/
  ./launch_backend
  if [[ ! $? -eq 0 ]]; then
    echo -e "\nunable to run container: $BACKEND_CONTAINER_ID"
    exit -1
  fi

  BACKEND_HOST=`get_container_IP $BACKEND_CONTAINER_ID`
  echo -e "\nDone! Go to http://$BACKEND_HOST/ to access your application"
}

status=`docker --version`
if [ $? -eq 0 ]; then
  ./cleanup_sarjitsu
  main
else
  echo "You don't have docker installed."
  echo "Run this again after installing docker"
fi
