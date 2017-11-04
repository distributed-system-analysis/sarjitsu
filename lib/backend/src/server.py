#!/usr/bin/env python3

import os
import sys
import requests
import configparser
from app import app, socketio#, reset_cache
from app.users.controller import *
from app.users.forms import UploadForm
from celery.task.control import inspect
from time import ctime
from flask import Flask, \
    jsonify, \
    render_template, \
    Response, \
    json, \
    make_response, \
    request, \
    redirect, \
    session, \
    abort, \
    send_from_directory
# user modules
from flask_socketio import emit
import upload_processor


config = configparser.ConfigParser()
config.read(app.config.get('CFG_PATH'))


@app.route('/asciimo', methods=['GET'])
def ascii():
    link = "http://i.imgur.com/kmbjB.png";
    return Response("<html><body><img src='%s'></body></html>" % link,
            mimetype='text/html')


@app.route('/', methods=['GET'])
def home():
    session['user'] = "anon"
    # reset_cache(session.sid)
    form = UploadForm(request.form)

    return render_template('index.html',
                                user=session['user'],
                                data=False,
                                form=form,
                                progress=0,
                                **app.config.get('TEMPLATE_CONFIGURATION'))


@app.route('/upload/', methods=['POST'])
def uploader():
    session['user'] = "anon"
    app.logger.info("current user <%s> for session ID: %s" %
                                    (session['user'], session.sid))
    file_list = []
    if request.method == 'POST':
        form = UploadForm(request.form)
        form.datafile = request.files.getlist("datafile")
        if form.validate_on_submit() or form.data['cmd_mode']:
            target =  os.path.join(app.cache.get('saDir').decode('utf-8'),
                                    session.sid)
            file_list = upload_processor.begin(target,session.sid, form)
            
        else:
            return jsonify({'form data': 'INVALID'})

        dashboard_url = config.get('Grafana','dashboard_url')
        if not dashboard_url:
            import socket; IP = socket.gethostbyname('frontend')
            dashboard_url = "http://%s:3000" % IP
        res = {
                "sessionID": session.sid,
                "user":session['user'],
                "redirect_url": dashboard_url,
                "file_count" : len(form.datafile),
                "file_list" : json.dumps(file_list)
            }
        if form.data['cmd_mode']:
            # res = {
            #     "valid_results": _valid_results_found,
            #     "data": response["nodenames_info"],
            #     "redirect_url": dashboard_url
            # }
            return jsonify(res)
        else:
            print(res)
            return render_template('results.html',
                data = res,
                **app.config.get('TEMPLATE_CONFIGURATION'))
            # return render_template('results.html',
            #     user=session['user'],
            #     # data=response["nodenames_info"],
            #     form=form,
            #     # valid_results=_valid_results_found,
            #     redirect_url=dashboard_url,
            #     progress=100,
            #     session_id=session.sid,
            #     **app.config.get('TEMPLATE_CONFIGURATION'))
    abort(405)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))


# @app.route('/<template>.html', methods=['GET'])
@app.route('/<template>/', methods=['GET'])
def template_loader(template='404'):
    session['user'] = "anon"
    # reset_cache(session.sid)
    form = UploadForm(request.form)

    try:
        return render_template('%s.html' % template,
                                user=session['user'],
                                data=False,
                                form=form,
                                progress=0,
                                **app.config.get('TEMPLATE_CONFIGURATION'))
    except:
        abort(404)

'''

Polls redis for results by opening a socketio connection
@param: 
@return:
@author: Geetika Batra

'''
@socketio.on('get results', namespace='/get_result')
def handle_results(json):
    poll_data = json
    sessionID = poll_data.get("sessionID", None)
    total_count = poll_data.get("total_count", None)
    file_list = poll_data.get("file_list", [])
    # redis_object = app.cache.hmget()
    # if sessionId!=None and total_count>0 and redis_object!=None:
    file_data = {}
    for each_file in file_list:
        search_key = "file_metadata:" + sessionID + ":" + each_file
        redis_object = app.cache.hgetall(search_key)
        redis_object = {k.decode(): v.decode() for k,v in redis_object.items()}
        file_data[search_key] = redis_object
    emit('response', file_data)

if __name__ == '__main__':
    try:

        socketio.run(app,
                host = app.config.get('HOST'),
                port = app.config.get('PORT'),
                debug = app.config.get('DEBUG'))
    except:
        raise
