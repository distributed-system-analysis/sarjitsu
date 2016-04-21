#DEPLOYMENT INSTRUCTIONS

- To build the image, refer:

```
docker build -t sarjitsu_elasticsearch .
```

- To run using the container, refer the following command:

```
docker run --privileged -it -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
```
