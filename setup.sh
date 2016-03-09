#!/bin/bash

root_dir=`echo $PWD`

cleanup(){
    CLEAN_IDS=$(docker ps -a | grep sarjitsu | awk -F' ' '{print $1}')
    if [[ ! -z $CLEAN_IDS ]]; then
	echo "cleaning up previously created sarjitsu instances"
	docker stop $CLEAN_IDS
	docker rm $CLEAN_IDS
    fi
}

main(){
    echo "building and running sarjitsu now"
    sleep 1
    cd ${root_dir%/}/datasource/
    docker build -t sarjitsu_elasticsearch .
    docker run --privileged -it -d \
	   -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch

    CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_elasticsearch | tail -n 1 | awk -F' ' '{ print $NF}'`
    DATASOURCE_IP=`docker inspect $CONTAINER_ID | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

    cd ${root_dir%/}/frontend/
    sed -i s/172.17.0.2/$DATASOURCE_IP/g conf/sar-index.cfg
    
    docker build -t sarjitsu_grafana .
    docker run --privileged -it -d \
	   -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_grafana

    CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_grafana | tail -n 1 | awk -F' ' '{ print $NF}'`
    FRONTEND_IP=`docker inspect $CONTAINER_ID | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

    cd ${root_dir%/}/backend/
    sed -i s/172.17.0.2/$DATASOURCE_IP/g conf/sar-index.cfg
    sed -i s/172.17.0.3/$FRONTEND_IP/g conf/sar-index.cfg
    docker build -t sarjitsu_backend .
    docker run --privileged -it -d \
	   -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend

    CONTAINER_ID=`docker ps --filter ancestor=sarjitsu_backend | tail -n 1 | awk -F' ' '{ print $NF}'`
    BACKEND_IP=`docker inspect $CONTAINER_ID | egrep '"IPAddress.*' | head -n 1 | awk -F'"' '{print $(NF-1)}'`

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
