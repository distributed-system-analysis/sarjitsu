#!/usr/bin/env python3

# updates grafana.ini with db credentials
# from sarjitsu.conf file (for postgres)

import os
import configparser

CONFIG_FILE='/etc/grafana/grafana.ini'
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# SARJITSU_CONF_PATH=os.path.join(BASE_DIR, '../../conf/sarjitsu.conf')

# with open(SARJITSU_CONF_PATH, 'r') as f:
#     c = f.read().splitlines()
#     # cleanup bash for comments / newlines
#     c = [i for i in c if not i.startswith('#')]
#     while '' in c:
#         c.remove('')
#     env_vars = dict([i.split('=') for i in c])

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

config['database']['type'] =  os.environ['GRAFANA_DB_TYPE']
config['database']['host'] = "%s:%s" % (os.environ['DB_HOST'],
                                        os.environ['DB_PORT'])
config['database']['name'] =  os.environ['DB_NAME']
config['database']['user'] =  os.environ['DB_USER']
config['database']['password'] =  os.environ['DB_PASSWORD']

with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)

print("updated grafana config..")
