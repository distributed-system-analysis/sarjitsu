#!/bin/bash

user_interrupt(){
  echo -e "\n\nKeyboard Interrupt detected."
  exit 1
}

trap user_interrupt SIGINT
trap user_interrupt SIGTSTP

ROOT_DIR=`echo $PWD`

source conf/sarjitsu.conf

cleanup(){
  CLEAN_IDS=$(docker ps -a | grep -P '^.*(\ssarjitsu.*|'$CONTAINER_ID_DASHBOARDS')$' | awk -F' ' '{print $1}')
  if [[ ! -z $CLEAN_IDS ]]; then
    echo "cleaning up previously created sarjitsu instances"
    docker stop $CLEAN_IDS
    docker rm $CLEAN_IDS
  fi
  rm -f ${ROOT_DIR%/}/conf/dashboard/db_environment
}

main(){
  echo "building and running sarjitsu now"
  sleep 1
  cd ${ROOT_DIR%/}/datasource/elasticsearch/
  echo "building sarjitsu_elasticsearch"
  docker build -t sarjitsu_elasticsearch . > /dev/null

  docker run --name $CONTAINER_ID_DASHBOARDS -e POSTGRES_PASSWORD=$DB_PASSWORD -e POSTGRES_USER=$DB_USER -d postgres
  if [[ ! $? -eq 0 ]]; then
    echo -e "\nunable to run container: $CONTAINER_ID_DASHBOARDS"
    exit -1
  fi

  docker run --name $CONTAINER_ID_ES --privileged -it -p 9400:9200 -d \
    -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
  if [[ ! $? -eq 0 ]]; then
    echo -e "\nunable to run container: $CONTAINER_ID_ES"
    exit -1
  fi

  # CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_elasticsearch | tail -n 1 | awk -F' ' '{ print $NF}'`
  DATASOURCE_IP=`docker inspect $CONTAINER_ID_ES | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`
  DASHBOARD_SOURCE_IP=`docker inspect $CONTAINER_ID_DASHBOARDS | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

  echo "storing credentials db_creds"
  cd ${ROOT_DIR%/}/conf/dashboard
  echo "DB_NAME=$DB_NAME" >> db_environment
  echo "DB_USER=$DB_USER" >> db_environment
  echo "DB_PASS=$DB_PASSWORD" >> db_environment
  echo "DB_TYPE=$GRAFANA_DB_TYPE" >> db_environment
  echo "DB_HOST=$DASHBOARD_SOURCE_IP" >> db_environment

  cd ${ROOT_DIR%/}/frontend/
  sed -i -r 's#^host\s?=.*#host = '$DATASOURCE_IP'#g' conf/sar-index.cfg

  echo "building sarjitsu_grafana"
  docker build -t sarjitsu_grafana . > /dev/null
  docker run  --name $CONTAINER_ID_FRONTEND --privileged -p 9500:3000 -it -d \
          -v ${ROOT_DIR%/}/conf/dashboard:/etc/sarjitsu \
          -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_grafana

  if [[ ! $? -eq 0 ]]; then
    echo -e "\nunable to run container: $CONTAINER_ID_FRONTEND"
    exit -1
  fi

  # CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_grafana | tail -n 1 | awk -F' ' '{ print $NF}'`
  FRONTEND_IP=`docker inspect $CONTAINER_ID_FRONTEND | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

  cd ${ROOT_DIR%/}/backend/
  sed -i -r 's#^host\s?=.*#host = '$DATASOURCE_IP'#g' conf/sar-index.cfg
  sed -i -r 's#^dashboard_url\s?=.*#dashboard_url = http://'$FRONTEND_IP':3000/#g' conf/sar-index.cfg
  sed -i -r 's#^api_url\s?=.*#api_url = http://'$FRONTEND_IP':5000/db/create/#g' conf/sar-index.cfg

  echo "building sarjitsu_backend"
  docker build -t sarjitsu_backend . > /dev/null
  docker run --name $CONTAINER_ID_BACKEND --privileged -p 9600:80 -it -d \
    -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend

  if [[ ! $? -eq 0 ]]; then
    echo -e "\nunable to run container: $CONTAINER_ID_BACKEND"
    exit -1
  fi

  # CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_backend | tail -n 1 | awk -F' ' '{ print $NF}'`
  BACKEND_IP=`docker inspect $CONTAINER_ID_BACKEND | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

  echo -e "\nDone! Go to http://$BACKEND_IP/ to access your application"
}

status=`docker --version`
if [ $? -eq 0 ]; then
  cleanup
  main
else
  echo "You don't have docker installed."
  echo "Run this again after installing docker"
fi
