# urgent

- [x] grafana - ES _msearch failure debug
- [x] push bc (build config) in $PROJECT_ROOT again
- [x] fix Dockerfile to set non-root edit permissions on /etc/elasticsearch.yml
  - [x] (and similarly for other containers where docker entrypoint is sed'g stuff) 
- [x] run services without systemd to streamline this with OSE cluster deployments where-in we won't run services in privileged mode 

# issues

- [x] bc manually set env vars. Ref: https://github.com/kubernetes-incubator/kompose/issues/406
- [x] tag manually while rolling out images

--

# pending

- [x] kompose
- [ ] include grafana PR #4694 as custom patch
- [x] docker-compose + custom hosts? (separate ES/postgres/grafana instances)
- [x] fix frontend url redirect linkage in uploaded results page

--

# feature request

- [ ] different sar file comparison feature
  - [ ] timeshift query support

--

# end goals

- [ ] pbench-sar https://github.com/distributed-system-analysis/pbench/pull/176
- [ ] vos-feedback + sarjitsu
