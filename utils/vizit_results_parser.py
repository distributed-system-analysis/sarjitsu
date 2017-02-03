#!/usr/bin/env python3

import sys
import json
from datetime import datetime
from prettytable import PrettyTable

fmt="%X, %d %b %Y"
PT = PrettyTable()
PT.field_names = ["Status", "Filename", "Platform", "Nodename", "Begin", "End"]

def tstos(date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return date.strftime(fmt)

def display_results(data):
    for item in data:
        tmp = item[:-1]
        try:
            tmp.append(tstos(item[-1]['grafana_range_begin']))
            tmp.append(tstos(item[-1]['grafana_range_end']))
        except:
            tmp.extend([item[-1]]*2)
        PT.add_row(tmp)


if __name__ == '__main__':
    try:
        curl_output = input()
        result = json.loads(curl_output)
        display_results(result['data'])
        print(PT)
        if result['valid_results']:
            print("\nGrafana Dashboard at: %s" %
                  result['redirect_url'])
            print("Login with your Grafana credentials [Default: (admin/admin)].\n")
        else:
            print("\nValid results NOT found; No Dashboards generated.")
        server_response_file = 'results.txt'
        with open(server_response_file, 'w') as f:
            f.write(str(PT)+"\n")
        print("..dumped results into %s" % server_response_file)

    except UnicodeDecodeError as e:
        print("UnicodeDecodeError: unable to parse output of curl for some reason.")
        print("\tERROR: %s" % e)
        server_response_file = 'response_log.txt'
        error_logfile = 'error.log'
        with open(server_response_file, 'w') as f:
            f.write(str(curl_output))
        with open(error_logfile, 'w') as f:
            f.write(str(e))
        print("..dumped server response into %s" % server_response_file)
        print("..dumped error log into %s" % error_logfile)
    except:
        raise
