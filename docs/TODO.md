- [ ] Add nested field templates
  - [ ] Add top 5 kinda agg stats for each nested doc type panel

- [ ] change mount point of postgres data to an external mount for persistent data

- [ ] consider using combination of following solutions for replication and service discovery
  - skydns/skydock, docker compose, zookeeper

- [ ] curl multi file upload check failure for *_conv files

- [ ] add condition in vizit for checking whether connection was reset by peer (in which case, the nodejs app restarts)
	and if so, re-upload the file

- [x] add backward compatibility for UPSERT in postgreSQL < 9.5
      otherwise we get: psycopg2.ProgrammingError: syntax error at or near "ON"

- [ ] add requirements.txt for elasticsearch python plugin

- [ ] add vizit documentation in README

- [ ] refactor vizit to be used as a separate client tool for uploading sa binaries

- [ ] fix -r option not working in vizit

- [ ] fix  $SUCCESS -eq 1 condition for displaying grafana login on vizit results, if some of the uploads pass

- [ ] update grafana to version 3 (branch arcolife/nested_agg_query) for nested docs support.
  - [ ] Make an rpm, release on copper and post link to PR on grafana)

- [ ] sar.data invalid files debug
