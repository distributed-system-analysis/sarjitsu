#!/usr/bin/env python3

import os
import sys
import requests
import configparser
from app import app#, reset_cache
from app.users.controller import *
from app.users.forms import UploadForm
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
import upload_processor
from config import \
    HOST, \
    PORT, \
    DEBUG,\
    TEMPLATE_CONFIGURATION


@app.route('/asciimo', methods=['GET'])
def ascii():
    link = "http://i.imgur.com/kmbjB.png";
    return Response("<html><body><img src='%s'></body></html>" % link,
            mimetype='text/html')


@app.route('/', methods=['GET'])
def home():
    session['user'] = "anon"
    # reset_cache(session.sid)
    app.logger.info("serving to user <%s> for session ID: %s" %
                                    (session['user'], session.sid))
    form = UploadForm(request.form)

    return render_template('index.html',
                                user=session['user'],
                                data=False,
                                form=form,
                                progress=0,
                                **TEMPLATE_CONFIGURATION)

@app.route('/page/<template>/', methods=['GET'])
def template_loader(template='index'):
    session['user'] = "anon"
    # reset_cache(session.sid)
    app.logger.info("serving %s.html to user <%s> for session ID: %s" %
                                    (template, session['user'], session.sid))
    form = UploadForm(request.form)

    try:
        return render_template('%s.html' % template,
                                user=session['user'],
                                data=False,
                                form=form,
                                progress=0,
                                **TEMPLATE_CONFIGURATION)
    except:
        abort(404)

@app.route('/upload/', methods=['GET','POST'])
def uploader():
    session['user'] = "anon"
    # reset_cache(session.sid)
    app.logger.info("current user <%s> for session ID: %s" %
                                    (session['user'], session.sid))
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        form = UploadForm(request.form)
        form.datafile = request.files.getlist("datafile")
        if form.validate_on_submit():
            target =  os.path.join(app.cache.get('saDir').decode('utf-8'),
                                    session.sid)
            result = upload_processor.begin(target, session.sid, form)
            if result == 500:
                abort(500)
            return jsonify(result)
        else:
            return jsonify({'form data': 'INVALID'})
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


if __name__ == '__main__':
    try:
        app.run(host = HOST,
                port = PORT,
                debug = DEBUG)
    except:
        raise
