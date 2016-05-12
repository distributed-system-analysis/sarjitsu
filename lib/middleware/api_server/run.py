#!/usr/bin/env python3

import ast
import os, sys
import configparser
import requests, json
from flask import Flask, jsonify, request, Response
from create_dashboard import *

app = Flask(__name__)

def _read_configs():
    cfg_name = "/etc/sar-index.cfg"
    config = configparser.ConfigParser()
    config.read(cfg_name)

    global SOURCE, TSTAMP_FIELD, TEMPLATES_PATH, API_PORT
    SOURCE = config.get('Grafana', 'ds_name')
    TSTAMP_FIELD = config.get('Grafana', 'timeField')
    TEMPLATES_PATH = os.path.join(config.get('Grafana', 'templates_path'),
                                'grafana', 'templates')
    API_PORT = config.get('Api','api_port')

    global db_credentials
    db_credentials = {}
    db_credentials['POSTGRES_DB_HOST'] = config.get('Postgres','db_host')
    db_credentials['POSTGRES_DB_PASS'] = config.get('Postgres','db_password')
    db_credentials['POSTGRES_DB_NAME'] = config.get('Postgres','db_name')
    db_credentials['POSTGRES_DB_USER'] = config.get('Postgres','db_user')
    db_credentials['POSTGRES_DB_PORT'] = config.get('Postgres','db_port')

    global default_modes
    default_modes = ['block_device', 'cpu_all', 'hugepages',
        'interrupts', 'io_transfer_rate_stats',
        'kernel_inode', 'load_avg', 'memory_page_stats',
        'memory_util', 'network', 'paging_stats',
        'proc_cswitch', 'swap_page_stats', 'swap_util', 'network']


@app.route('/', methods=['GET'])
def home():
    return jsonify({'api_test': 'OK'})


@app.route('/test/client/', methods=['POST'])
def test():
    print(request.data)
    return jsonify({'got response from server': 'OK'})


@app.route('/db/create/', methods=['POST', 'GET'])
def create_db():
    if request.method  == 'GET':
        ts_beg = request.args.get('ts_beg')
        ts_end = request.args.get('ts_end')
        nodename = request.args.get('nodename')
        modes = request.args.get('modes')
    elif request.method  == 'POST':
        ts_beg = request.json.get('ts_beg', '')
        ts_end = request.json.get('ts_end', '')
        nodename = request.json.get('nodename', '')
        modes = request.json.get('modes', '')
    else:
        txt = "only GET/POST requests are allowed on this endpoint"
        response = { "reply" : "FAILED",
                    "response": txt}
        status=405
        resp = Response(json.dumps(response),
                        status=status,
                        mimetype='application/json')
        return resp

    if not modes:
        modes=default_modes

    if ts_beg and ts_end and nodename:
        try:
            beg, end = tstos(ts_beg=ts_beg, ts_end=ts_end)
            date = beg.split()[0]
            PP = PrepareDashboard(DB_TITLE='%s_%s_investigation' % (nodename, date),
                                  DB_TITLE_ORIG='%s_%s_investigation' % (
                                      nodename, date),
                                  _FROM=beg, _TO=end,
                                  _FIELDS=modes.split(','),
                                  NODENAME=nodename,
                                  TIMEFIELD=TSTAMP_FIELD,
                                  TEMPLATES=TEMPLATES_PATH,
                                  db_credentials=db_credentials,
                                  DATASOURCE=SOURCE)

            PP.store_dashboard()
            response = { "reply" : "SUCCESS",
                        "response": "dashboard created for %s" % (nodename)}
            status=200
        except ValueError:
            txt = "dashboard could not be created. Check arg values supplied"
            response = { "reply" : "FAILED",
                        "response": txt}
            status=400
        except Exception as E:
            print("ERROR: %s" % E)
            txt = "unknown exception encountered while processing"
            response = { "reply" : "FAILED",
                        "response": txt}
            status=500
    else:
        response = { "reply" : "FAILED! check arguments",
                    "required_args" : "ts_beg, ts_end, nodename (all strings)",
                    "options_args" : "modes (comma separated list)"}
        status=400

    resp = Response(json.dumps(response),
                    status=status,
                    mimetype='application/json')
    return resp


if __name__ == '__main__':
    try:
        _read_configs()
        app.run(host = '0.0.0.0',
                port = API_PORT,
                debug = False)
    except:
        raise
