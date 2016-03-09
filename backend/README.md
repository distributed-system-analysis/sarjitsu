#DEPLOYMENT INSTRUCTIONS

NOTE: Before building, ensure that you have set the correct URLs of
      ElasticSearch and Grafana instances under backend/conf/sar-index.cfg
      
- To build the image, refer:

```
docker build -t sarjitsu_backend .
```

- To run using the container, refer the following command:

```
docker run --privileged -it -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend
```
