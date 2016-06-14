#!/usr/bin/env python3

import sys
import json
from prettytable import PrettyTable

def display_results(data):
    x = PrettyTable()
    x.field_names = ["Status", "Filename", "Platform",
                     "Nodename", "Begin", "End"]
    for item in data:
        tmp = item[:-1]
        try:
            tmp.append(item[-1]['grafana_range_begin'])
            tmp.append(item[-1]['grafana_range_end'])
        except:
            tmp.extend(["Invalid Input", "Invalid Input"])
        x.add_row(tmp)

    print(x)
    
if __name__ == '__main__':
    INPUT_FILE = sys.argv[1]
    result = json.load(open(INPUT_FILE, 'r'))
    display_results(result['data'])
    print("\nGrafana Dashboard at: %s" %
          result['redirect_url'])
    print("\nValid results found: %s" %
          result['valid_results']) 
