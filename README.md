Sarjitsu
========

Sarjitsu ingests a SAR (System Activity Reporter) binary data file of any
format and produces dynamic visualizations based on Grafana. The name is inspired from 'SAR + jistsu',
so to speak, unleashing the power of SAR data.

The app is split in 3 container instances as follows:

1) `datasource`: A full-text search engine powered by elasticsearch

2) `frontend`: A dynamic visualization front, which performs 2 duties:

- sourcing data from elasticsearch
- building visualization dashboards from an API endpoint,
  hosted on this container

3) `backend`: A NodeJS based web app, which runs the web interface for users
   	    to upload a SA binary file and obtain visualizations.

- `backend` is responsible for indexing data in `datasource`
  and for throwing metadata at `frontend`.
- `frontend` builds dashboards based on data from `backend`
  and connects to `datasource` for displaying dashboards.

## INSTALLATION

### For the impatient:

- single step setup script  `$ ./setup.sh`

WARNING: This script would remove all previously running instances of sarjitsu.

### Installing by customizing the modularized components, per say, having their own IPs:

- Step 0: Make sure you have [docker](https://www.docker.com/) installed.

- Step 1: Build and run `datasource` container from `datasource/` directory:

  ```
  $ docker build -t sarjitsu_elasticsearch .
  $ docker run --privileged -it -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
  ```

  Note down the IP address of of ElasticSearch container: `docker inspect <container ID>  | grep IP`

- Step 2: Change the IP noted in previous step, inside `frontend/conf/sar-index.cfg` as follows:

	 ```
	 [ElasticSearch]
	 host = <datasource container IP>
	 port = 9200
	 protocol = http
	 ```

- Step 3: Build and run `frontend` container from `frontend/` directory:

  ```
  $ docker build -t sarjitsu_grafana .
  $ docker run --privileged -it -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_grafana
  ```

  Note down the IP address of of `frontend` container: `docker inspect <container ID>  | grep IP`

- Step 4: Change the IP noted in previous step, inside `backend/conf/sar-index.cfg` as follows:

	 ```
	 [ElasticSearch]
	 host = <datasource container IP>
	 port = 9200

	 [Grafana]
	 dashboard_url=http://<frontend container IP>:3000/
	 api_url=http://<frontend container IP>:5000/db/create/
	 ```

- Step 5: Build and run `backend` container from `backend/` directory:

  ```
  $ docker build -t sarjitsu_backend .
  $ docker run --privileged -it -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend
  ```

  Note down the IP address of of `backend` container: `docker inspect <container ID>  | grep IP`

- Step 6: Access the application at `http://<backend container IP>`

Optional: `-p 9210:80` supply this to docker run command to map the
	  container's internal port 80 to host's port 9210 for external access.
	  
## APP FLOW

```
SA Binary upload --> Comptability checks and conversion (if needed)
--> Conversion to a temporary XML output --> ingestion into Elasticsearch
--> Creation of dashboard from metadata about the SAR data -->
Upload finished and grafana dashboard generated --> Output tagged with
the appropriate nodename to which the data belongs, along with the datetime
range it was recorded for.
```

It segragates the data into various panels in the grafana dashboard, based on
params like CPU, Disk, Network usage.

Description of those parameters could be obtained in detail by running
the command `$ man sar` on a linux terminal. Or you could read about them
[here on the official man page for sar command](http://linux.die.net/man/1/sar)

## FAQs

- How is it unique compared to other existing solutions?

  What sarjitsu does, is it gives you the unique ability throw in any version of
  `sa binary files` from your system's `/var/log/sa/` folder, to produce visualizations
  with all the SAR params supported till date. This makes it much easier for a user
  to go see what's wrong / different about the system behavior by instantly getting
  access to all the data indexed in a nice NoSQL based full-text search engine and
  a dynamic visualization playground. It further simplifies this process by providing
  a web interface to upload these files to!

  Sarjitsu also automatically detects the time range of the sa files to display the
  time-series visualizations and names the dashboards based on the nodename of your system.

  It is not tied to a specific machine, but is an independent solution, as a web app.

- Is it portable/scalable ?

  Sarjitsu is scalable since it keeps the datasource, frontend and backend separately
  and is based on completely scalable and portable solution, i.e., Elasticsearch,
  Grafana and NodeJs ..in their respective containerized environments using Docker.
