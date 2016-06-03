# import ast
import requests
import configparser
from app import app

config = configparser.ConfigParser()

def dashboard(hostname, sar_params, time_range):
    config.read(app.config.get('CFG_PATH'))
    api_endpoint = config.get('Grafana','api_url')

    payload = {
        "ts_beg": time_range['grafana_range_begin'],
        "ts_end": time_range['grafana_range_end'],
        "nodename": hostname,
        "modes": sar_params
    }

    try:
        res = requests.post(api_endpoint, data=payload)
        if res.status_code == 200:
            app.logger.info("status code: %s" % res.status_code)
            app.logger.info("content: \n%s" % res.content)
            app.logger.info("Dashboard created for -- %s" % hostname);
        else:
            app.logger.warn("status code: %s" % res.status_code)
            app.logger.warn("content: \n%s" % res.content)

    except ConnectionError:
        app.logger.error("endpoint not active. Couldn't connect.")
    except:
        app.logger.error("unknown error. Couldn't trigger request.")

    return
