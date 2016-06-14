#!/usr/bin/env python3

import sys
import json
from datetime import datetime
from prettytable import PrettyTable

fmt="%X, %d %b %Y"
PT = PrettyTable()
PT.field_names = ["Status", "Filename", "Platform",
"Nodename", "Begin", "End"]

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
    result = json.loads(input())
    display_results(result['data'])
    print(PT)
    if result['valid_results']:
        print("\nGrafana Dashboard at: %s" %
              result['redirect_url'])
        print("Login with your Grafana credentials. [Default: (admin/admin)]\n")
    else:
        print("\nValid results NOT found; No Dashboards generated.")
