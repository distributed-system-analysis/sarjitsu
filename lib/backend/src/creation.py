import ast
import requests
import configparser
from app import app

config = configparser.ConfigParser()

def dashboard(hostname, sar_params, ts_beg, ts_end):
    config.read(app.config.get('CFG_PATH'))
    api_endpoint = config.get('Grafana','api_url')
    # import pdb; pdb.set_trace()

    payload = {
        "ts_beg": ts_beg,
        "ts_end": ts_end,
        "nodename": hostname,
        "modes": ast.literal_eval(sar_params)
    }

    try:
        res = requests.post(api_endpoint, data=payload)
    except ConnectionError:
        app.logger.error("endpoint not active. Couldn't connect.")
    except:
        app.logger.error("unknown error. Couldn't trigger request.")

    if res.status_code == 200:
        app.logger.info("status code: %s" % res.status_code)
        app.logger.info("content: \n%s" % res.content)
        app.logger.info("Dashboard created for -- %s" % hostname);
    else:
        app.logger.warn("status code: %s" % res.status_code)
        app.logger.warn("content: \n%s" % res.content)

    return
