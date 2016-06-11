- [x] curl multi file upload check failure for *_conv files

- [x] add backward compatibility for UPSERT in postgreSQL < 9.5
      otherwise we get: psycopg2.ProgrammingError: syntax error at or near "ON"

- [x] sar.data invalid files debug

- [X] copy config files for ES, grafana as well.
- [X] switch to sabinary detection
- [X] integrate sar ES indexing
- [X] Devise method to specify config for sarjitsu
- [X] handle the error in case sa binary not compatible.
- [X] debug why only cpu-load is getting indexed in ES
- [X] change sarjitsu to generate grafana templates from options selected
	- [X] store templates as dashboards in `dashboard` table in `/var/lib/grafana/grafana.db`
	- [X] store datasource in 'data_source'
	- [X] debug modes.json options (some of them don't work)
	- [X] switch to `sar_args_mapping.json`

- [X] finish create_dashboard script and integrate with server.js
- [X] devise method to graph stats dynamically

- [X] fix es-create template/mapping for all pattern sar indices

- [X] fix app crash on second upload

- [X] fix stdOut clearance on second upload. double 'parsin ...' messages

- [X] restore session functionality

- [X] replace txt on /upload page with something useful / redirect to dashboard directly

- [X] magic code for f22/23 absent in sadf
	- `stderr: Invalid - safiles/1/sa18/sa18: Unrecognized new format magic: 0x8563`

- [x] implement check_previous() <metadata> to assign proper versions/dashboard IDs

- [X] assign same name to db-slug and db-name

- [x] sadf detect option failure (i.e. if 1 out of 3 options didn't work, whole script fails)
	This has been fixed using silent failure feature in newer sadf versions. So
	- [x] process all and select later while building dashboard


- [x] debug env var not working issue for config path
- [x] add support for 'Multiple option <nested ones>' args in sar
- [x] debug templating in grafana. Check format in sqlite3 db
- [x] fix panel collapse error in grafana (for readymade panels)
- [x] add error handling, in case data for that arg is not present
- [ ] add unit tests
- [X] improve error log quality (remove curl outputs from ES queries / append -s to curl)
	- [X] switch to python based ES queries instead of curl

- [x] separate ES, grafana and sarjitsu backend in 3 separate containers.
