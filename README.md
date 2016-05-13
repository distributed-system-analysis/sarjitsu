Sarjitsu
========

Sarjitsu ingests a SAR (System Activity Reporter) binary data file of any
format and produces dynamic visualizations based on Grafana. The name is inspired from 'SAR + jistsu',
so to speak, unleashing the power of SAR data.

The app is split in 5 container instances as follows:

1) `datasource`: Used to store timeseries data and metadata. A full-text search engine powered by elasticsearch

2) `metricstore`: Postgres powered, used by the frontend (grafana in our case) to store metadata about dashboards, datasource and users.

3) `frontend`: Powered by Grafana, a dynamic visualization frontend, which performs 2 duties; sources data from elasticsearch

4) `middleware`: A Python-Flask powered API that talks to backend and metricstore; builds scriped dashboards

5) `backend`: A NodeJS based web app, which runs the web interface
              for users to upload a SA binary file and obtain visualizations.


Application flow is explained in detail in the section `APP FLOW` below.

## INSTALLATION

- Step 0: Make sure you have [docker](https://www.docker.com/) installed.

### For the impatient:

- single step setup script  `$ ./setup.sh`

WARNING: This script would remove all previously running instances of sarjitsu.

Be sure to run `# iptables -F` from the host, in case it's not accessible outside.
Otherwise check your firewall settings.

- To stop all running container instances and cleanup sarjitsu, run `$ ./cleanup_sarjitsu`

### For the ones who've found inner peace:

Installing by customizing the modularized components, per say, having their own IPs. 

- Step 1: open `conf/sarjitsu.conf` and edit the params as required. If for example,
          you don't want to spawn containers for postgres, grafana or elasticsearch,
          you should leave out their `*_HOST` parameters empty.

  ```sh
  # metricstore config (postgres) - for grafana's metadata
  DB_HOST=
  # append DB_PORT in grafana.ini db config
  DB_NAME=grafana
  DB_USER=grafana
  DB_PASSWORD=sarjitsu123
  DB_PORT=5432 # default for postgres

  # datasource config (elasticsearch) - source of timeseries data
  ES_HOST=172.17.0.3
  ES_PORT=9200

  # frontend config (grafana) - visualization framework
  GRAFANA_HOST=
  GRAFANA_DB_TYPE=postgres

  # make sure this is above 1024; 3000 is standard
  GRAFANA_PORT=3000
  ```

  This is minimal config needed to take a look over. Leave the rest of the parameters
  unchanged, if you're unsure.

- Step 2: After you're sure your configurations are alright, simply run setup.sh

  ```sh
  $ ./setup.sh
  ```

Building this first time would take some time, as docker images are pulled from dockerhub,
customized and built, packages are installed and so on..

At the end, though, it should output a message like:
```
Done! Go to http://172.17.0.6:80/ to access your application
```

If it fails in between, you might wanna take a look at your configurations / environment.
If you think it's a bug, you're welcome to open an issue here on github.

### Additional Note

- Below mentioned ports will be used for port mapping from container to host, and
  could be configured in `conf/sarjitsu.conf`. Default bindings are:

  ```sh
  METRICSTORE_PORT_MAPPING=9600
  DATASOURCE_PORT_MAPPING=9601
  FRONTEND_PORT_MAPPING=9602
  MIDDLEWARE_PORT_MAPPING=9603
  BACKEND_PORT_MAPPING=9604
  ```
  This is when all components are containerized.

## APP FLOW

### Architecture

From `docs/sarjitsu_architecture.png`:

![arch](https://raw.githubusercontent.com/arcolife/sarjitsu/master/docs/sarjitsu_architecture.png)

### Control Flow

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
  and is based on completely scalable and portable solution, i.e., Elasticsearch, Postgres, Grafana and NodeJs ..in their respective containerized environments using Docker.
