Sarjitsu
========

Sarjitsu ingests a SAR (System Activity Reporter) binary data file of any
format and produces dynamic visualizations based on Grafana. The name is inspired from 'SAR + jistsu',
so to speak, unleashing the power of SAR data.

The app is split in 3 major container instances as follows:

1) `datasource`: Used to store data and metadata. Has 2 types:

  a. `elasticsearch`: A full-text search engine powered by elasticsearch

  b. `postgres`:  A metric store, used by the frontend (grafana in our case)
                  to store metadata about dashboards, datasource and users.

2) `frontend`: A dynamic visualization frontend, which performs 2 duties:

  - sourcing indexed data from elasticsearch

  - building visualization dashboards from an API endpoint, hosted on this container

3) `backend`: A NodeJS based web app, which runs the web interface
                      for users to upload a SA binary file and obtain visualizations.

Application flow is explained in detail in the section `APP FLOW` below.

## INSTALLATION

### For the impatient:

- single step setup script  `$ ./setup.sh`

WARNING: This script would remove all previously running instances of sarjitsu.

Your containers would be mapped to the ports on the host as per following default settings:

- Elasticsearch, accessible at http://localhost:9400
- Frontend, accessible at http://localhost:9500
- Landing page (backend), accessible at http://localhost:9600

Replace localhost with your <host IP>, if you need remote access. Be sure to
run `# iptables -F` from the host, in case it's not accessible outside. Otherwise
check your firewall settings.


### For the ones who've found inner peace:

#### Installing by customizing the modularized components, per say, having their own IPs:

Let ROOT_DIR be this project root containing the `setup.sh` script in this repo.

- Step 0: Make sure you have [docker](https://www.docker.com/) installed.

- Step 1: Make sure you have following references defined in your bash env:

  ```
  # optional: static names for your containers.
  CONTAINER_ID_ES='elastic_jitsu'
  CONTAINER_ID_FRONTEND='grafana_jitsu'
  CONTAINER_ID_BACKEND='node_jitsu'
  CONTAINER_ID_DASHBOARDS='postrgres_jitsu'

  # postgres db credentials
  GRAFANA_DB_TYPE='postgres'
  DB_USER='arco'
  DB_NAME='arco'
  DB_PASSWORD='test123'
  ```

  We would use these refs in rest of deployment steps. Change these accordingly.

- Step 2: Build and run `datasource` containers from `datasource/` directory:

  - To store dashboards, we would need a postgres container:

  ```
  docker run --name $CONTAINER_ID_DASHBOARDS -e POSTGRES_PASSWORD=$DB_PASSWORD -e POSTGRES_USER=$DB_USER -d postgres
  ```

  - To store and query SAR data, we need an elasticsearch container instance:
  ```
  $ cd ${ROOT_DIR%/}/datasource/elasticsearch/
  $ docker build -t sarjitsu_elasticsearch .
  $ docker run --name $CONTAINER_ID_ES --privileged -it -p 9400:9200 -d \
      -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_elasticsearch
  ```

  Note down the IP address of these 2 datasource containers: `docker inspect <container ID/NAME>  | grep IP`

- Step 2: Change the IP noted in previous step, inside `frontend/conf/sar-index.cfg` as follows:

	 ```
	 [ElasticSearch]
	 host = <datasource container IP>
	 port = 9200
	 protocol = http
	 ```

- Step 3: Build and run `frontend` container from `frontend/` directory:

  Before you build the frontend image:

  a. generate the config file under `${ROOT_DIR%/}/conf/dashboard` as follows:

  ```
  echo "DB_NAME=$DB_NAME" >> db_environment
  echo "DB_USER=$DB_USER" >> db_environment
  echo "DB_PASS=$DB_PASSWORD" >> db_environment
  echo "DB_TYPE=$GRAFANA_DB_TYPE" >> db_environment
  echo "DB_HOST=$DASHBOARD_SOURCE_IP" >> db_environment
  ```

  b. Change frontend config file `${ROOT_DIR%/}/frontend/conf/sar-index.cfg` as follows:
  ```
  [ElasticSearch]
  host = <DATASOURCE_IP>
  port = 9200
  protocol = http
  ...
  ```

  c. Then build the container from `$ROOT_DIR`:

  ```
  $ docker build -t sarjitsu_grafana .
  $ docker run  --name $CONTAINER_ID_FRONTEND --privileged -p 9500:3000 -it -d \
          -v ${ROOT_DIR%/}/conf/dashboard:/etc/sarjitsu \
          -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_grafana
  ```

  Note down the IP address of of `frontend` container: `docker inspect <container ID>  | grep IP`

- Step 4: Change the IP noted in previous step, inside `backend/conf/sar-index.cfg` as follows:

  ```
  [ElasticSearch]
  host = <datasource container IP>
  port = 9200

  [Grafana]
  dashboard_url = http://<frontend container IP>:3000/
  api_url = http://<frontend container IP>:5000/db/create/
  ```

  Keep the whitespaces in `key = value` intact, as illustrated above.

  NOTE: Sarjitsu uses default postgres port for connection. If you'd like to change that,
  change the call to database in `psycopg2.connect` under `frontend/api_server/create_dashboard.py`
  and rebuild `frontend` instance.

- Step 5: Build and run `backend` container from `backend/` directory:

  ```
  $ docker build -t sarjitsu_backend .
  $ docker run --name $CONTAINER_ID_BACKEND --privileged -p 9600:80 -it -d \
      -v /sys/fs/cgroup:/sys/fs/cgroup:ro sarjitsu_backend
  ```

  Note down the IP address of of `backend` container: `docker inspect <container ID>  | grep IP`

- Step 6: Access the application at `http://<backend container IP>` or at `http://localhost:9600` (or <host IP>:9600)


NOTE: `-p 9600:80` when supplied to `docker run` command, maps container's internal port 80
      to host's port 9210 to facilitate remote access to the same.

## APP FLOW

### Container connotations:

1. datasources:
  a. sarjitsu_elasticsearch
  b. postgres

2. frontend: sarjitsu_grafana
3. backend: sarjitsu_backend

---

### The flow:

- `backend` is responsible for indexing data in `datasource`
and for throwing metadata at `frontend`.
- `frontend` builds dashboards based on data from `backend`
and connects to `datasource` for displaying dashboards.

#### Control Flow

Following steps involved in visualizing SA binary file:

- Step 1: SA Binary upload --> Comptability checks and conversion (if needed)
- Step 2: Conversion to a temporary XML output --> ingestion into Elasticsearch
- Step 3: Creation of dashboard from metadata about the SAR data (time range inferred)
- Step 4: Grafana dashboard generated --> Output tagged with the appropriate nodename


Sarjitsu's frontend service segragates data into various panels, based on params like CPU, Disk, Network usage.

Description of those parameters could be obtained in detail by running the command `$ man sar` on a linux terminal. Or you could read about them [here on the official man page for sar command](http://linux.die.net/man/1/sar)

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
