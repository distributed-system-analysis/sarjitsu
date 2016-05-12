#DEPLOYMENT INSTRUCTIONS

- To run using the container, refer the following command:
```
docker run --name <postgres_jistu> \
       -e POSTGRES_PASSWORD=<psql_password> \
       -e POSTGRES_USER=<psql_username> \
       -e POSTGRES_DB=<psql_db_name> \
       -d postgres
```
