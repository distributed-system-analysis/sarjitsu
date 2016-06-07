import os
import sys
import redis
import logging
import datetime
from time import ctime
from urllib.parse import urljoin
from flask import Flask, render_template, json, session

from logging.handlers import RotatingFileHandler
from flask_session import RedisSessionInterface

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,  template_folder=os.path.join(BASE_DIR, 'templates'))
app.config.from_object('config')

SAR_ARGS = os.path.join(BASE_DIR, 'static/sar_args_mapping.json')
sar_modes = json.load(open(SAR_ARGS, 'r'))

SA_DIR = app.config.get("SA_DIR")
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
# handler = TimedRotatingFileHandler('logs/foo.log', when='midnight', interval=1)
handler = RotatingFileHandler(app.config.get('LOG_FILENAME'),
                            maxBytes=app.config.get('LOG_FILESIZE'),
                            backupCount=1)
# handler.setLevel(logging.INFO)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.DEBUG)
# log.addHandler(handler)

app.cache = redis.StrictRedis(**app.config.get('REDIS_CONFIG'))

app.cache.set("saDir", SA_DIR)
app.cache.set("uid_track", 1)
app.cache.set("session_data", {})

app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + SA_DIR
app.config['STATIC_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '/static'

# app.session_interface = RedisSessionInterface(app.cache, key_prefix='SESSION')
app.session_interface = RedisSessionInterface(app.cache, key_prefix='SESSION',
                                            use_signer=True, permanent=False)
app.permanent_session_lifetime = datetime.timedelta(hours=1)

try:
    os.mkdir(SA_DIR)
except Exception as E:
    app.logger.info("[%s] mkdir() -- [%s] : %s" % \
                        (ctime(), SA_DIR, E))

# def reset_cache(sessionID):
#     session_data = {
#         "false_upload": True,
#         # "stdOut": '',
#         # "stdOut_conv": ''
#     }
#     app.cache.hmset("session_data:%s" % sessionID, session_data)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Sample HTTP error handling
@app.errorhandler(500)
def not_found(error):
    return render_template('500.html',
                           user=session['user'],
                           header_text=app.config['TEMPLATE_CONFIGURATION']['header_text'],
                           title=app.config['TEMPLATE_CONFIGURATION']['header_text']), 500

def _jinja2_filter_list(item, n):
    """ return N  no. of items in history list """
    return item[:n]

def _jinja2_filter_datetime(date, fmt="%X, %d %b %Y"):
    # check whether the value is a datetime object
    if not isinstance(date, (datetime.date, datetime.datetime)):
        try:
            date = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            return date
    return date.strftime(fmt)

def _jinja2_filter_url(link_name, path):
    """ get full url of MarkDown file """
    return urljoin(path, link_name)

app.jinja_env.filters['datetime'] = _jinja2_filter_datetime
app.jinja_env.filters['arrange'] = _jinja2_filter_list
app.jinja_env.filters['urljoin'] = _jinja2_filter_url
