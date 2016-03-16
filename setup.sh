#!/bin/bash

user_interrupt(){
    echo -e "\n\nKeyboard Interrupt detected."
    exit 1
}

trap user_interrupt SIGINT
trap user_interrupt SIGTSTP

ROOT_DIR=`echo $PWD`

CONTAINER_ID_ES='elastic_jitsu'
CONTAINER_ID_FRONTEND='grafana_jitsu'
CONTAINER_ID_BACKEND='node_jitsu'
CONTAINER_ID_DASHBOARDS='postrgres_jitsu'

GRAFANA_DB_TYPE='postgres'
DB_USER='arco'
DB_NAME='arco'
DB_PASSWORD='test123'

cleanup(){
    CLEAN_IDS=$(docker ps -a | grep -P '^.*(\ssarjitsu.*|'$CONTAINER_ID_DASHBOARDS')$' | awk -F' ' '{print $1}')
    if [[ ! -z $CLEAN_IDS ]]; then
    	echo "cleaning up previously created sarjitsu instances"
    	docker stop $CLEAN_IDS
    	docker rm $CLEAN_IDS
    fi
}

main(){
    echo "building and running sarjitsu now"
    sleep 1
    cd ${ROOT_DIR%/}/datasource/elasticsearch/
    docker build -t sarjitsu_elasticsearch .

    docker run --name $CONTAINER_ID_DASHBOARDS -e POSTGRES_PASSWORD=$DB_PASSWORD -e POSTGRES_USER=$DB_USER -d postgres

    docker run --name $CONTAINER_ID_ES --privileged -it -d \
	   -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch

    # CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_elasticsearch | tail -n 1 | awk -F' ' '{ print $NF}'`
    DATASOURCE_IP=`docker inspect $CONTAINER_ID_ES | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`
    DASHBOARD_SOURCE_IP=`docker inspect $CONTAINER_ID_DASHBOARDS | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

    cd ${ROOT_DIR%/}/frontend/
    sed -i -r 's#^host\s?=.*#host = '$DATASOURCE_IP'#g' conf/sar-index.cfg
    sed -i -r 's#^postgres_host\s?=.*#postgres_host = '$DASHBOARD_SOURCE_IP'#g' conf/sar-index.cfg

    docker build -t sarjitsu_grafana .
    docker run  --name $CONTAINER_ID_FRONTEND --privileged -it -d \
                            -e DB_TYPE=$GRAFANA_DB_TYPE \
                            -e DB_HOST=$DASHBOARD_SOURCE_IP \
                            -e DB_NAME=$DB_NAME \
                            -e DB_USER=$DB_USER \
                            -e DB_PASSWORD=$DB_PASSWORD \
	                          -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_grafana

    # CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_grafana | tail -n 1 | awk -F' ' '{ print $NF}'`
    FRONTEND_IP=`docker inspect $CONTAINER_ID_FRONTEND | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

    cd ${ROOT_DIR%/}/backend/
    sed -i -r 's#^host\s?=.*#host = '$DATASOURCE_IP'#g' conf/sar-index.cfg
    sed -i -r 's#^dashboard_url\s?=.*#dashboard_url = http://'$FRONTEND_IP':3000/#g' conf/sar-index.cfg
    sed -i -r 's#^api_url\s?=.*#api_url = http://'$FRONTEND_IP':5000/db/create/#g' conf/sar-index.cfg
    docker build -t sarjitsu_backend .
    docker run --name $CONTAINER_ID_BACKEND --privileged -it -d \
	   -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend

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
