#!/bin/env node

var express = require('express'),
    os = require('os'),
    fs = require('fs'),
    path = require('path'),
    util = require('util'),
    _process = require('child_process'),
    upload_file = require('./upload.js'),
    create = require('./creation.js'),
    session = require('express-session'),
    FileStore = require('session-file-store')(session),
    zcache;

/**
 *  Populate the cache.
 */
populateCache = function() {
    if (typeof zcache === "undefined") {
        zcache = {
            "saDir": "safiles",
            "uid_track": 1,
            "index.html": "",
            "session_data": {}
        };
    }

    //  Local cache for static content.
    zcache['index.html'] = fs.readFileSync('./public/index.html');
};


/**
 *  Retrieve entry (content) from cache.
 *  @param {string} key  Key identifying content to retrieve from cache.
 */
cache_get = function(key) { return zcache[key]; };


var SarjitsuApp = function() {

    //  Scope.
    var self = this;

    /*  ================================================================  */
    /*  Helper functions.                                                 */
    /*  ================================================================  */

    /**
     *  Set up server IP address and port # using env variables/defaults.
     */
    self.setupVariables = function() {
        //  Set the environment variables we need.
        process.env['pbench_tspp_dir'] = path.resolve(__dirname, 'scripts');
        self.ipaddress = process.env.OPENSHIFT_NODEJS_IP;
        self.port      = process.env.OPENSHIFT_NODEJS_PORT || 80;

        if (typeof self.ipaddress === "undefined") {
            //  Log errors on OpenShift but continue w/ 0.0.0.0 - this
            //  allows us to run/test the app locally.
            console.warn('No OPENSHIFT_NODEJS_IP var, using 0.0.0.0');
            self.ipaddress = "0.0.0.0";
        };
    };


    /**
     *  terminator === the termination handler
     *  Terminate server on receipt of the specified signal.
     *  @param {string} sig  Signal to terminate on.
     */
    self.terminator = function(sig){
        if (typeof sig === "string") {
           util.log('Received %s - terminating Sarjitsu app ...' + sig);
           process.exit(1);
        }
        util.log('Node server stopped.');
    };


    /**
     *  Setup termination handlers (for exit and a list of signals).
     */
    self.setupTerminationHandlers = function(){
        //  Process on exit and signals.
        process.on('exit', function() { self.terminator(); });

        // Removed 'SIGPIPE' from the list - bugz 852598.
        ['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT',
         'SIGBUS', 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGTERM'
        ].forEach(function(element, index, array) {
            process.on(element, function() { self.terminator(element); });
        });
    };


    /*  ================================================================  */
    /*  App server functions (main app logic here).                       */
    /*  ================================================================  */

    /**
     *  Create the routing table entries + handlers for the application.
     */
    self.createRoutes = function() {
        self.routes = { };

        self.routes['/asciimo'] = function(req, res) {
            var link = "http://i.imgur.com/kmbjB.png";
            res.send("<html><body><img src='" + link + "'></body></html>");
        };

        self.routes['/user/:uid/:tag/csv/:datafile'] = function(req,res) {
            var datafile_src = path.join(__dirname, 'safiles', req.params.uid, req.params.tag, 'csv', req.params.datafile);
            res.sendfile(datafile_src);
        };

        self.routes['/user/:uid/:tag/'] = function(req,res) {
            if (zcache["session_data"][req.sessionID]) {
                if (zcache["session_data"][req.sessionID]['uid'] == req.params.uid) {
                    var result_path = path.join(__dirname, 'safiles', req.params.uid, req.params.tag, 'index.html');
                    fs.exists(result_path, function(exists) {
                        if(exists) {
                            res.sendfile(result_path);
                        } else {
                            res.status(404)        // HTTP status 404: NotFound
                                .send('Bummer.. This record does not exist!!');
                        }
                    });

                } else {
                    res.status(550)        // HTTP status 404: NotFound
                       .send('Not Allowed: You are trying to access another user\'s files!');
                }
            } else {
                res.status(404)        // HTTP status 404: NotFound
                    .send('Bummer.. This user account does not exist!!');
            }
        };

        self.routes['/upload'] = function(req, res, next) {

            initiateUpload(function(upload_dir_path) {
                fs.mkdir(zcache["session_data"][req.sessionID]["upload_dir_path"], function(error) {
                    if (error) {
                        util.log('mkdir() -- [' + zcache["session_data"][req.sessionID]["upload_dir_path"] + '] : ' + error);
                    }
                    upload_file.begin(req, res, next, _process, util, create, zcache);
                });
            });

            function initiateUpload(callback) {
                if (zcache["session_data"][req.sessionID]) {
                    zcache["session_data"][req.sessionID]["fields"] = [];
                    zcache["session_data"][req.sessionID]["argOfsar"] = '';
                    zcache["session_data"][req.sessionID]["sa_file_path"] = null;
                    zcache["session_data"][req.sessionID]["sadf_type_det"] = null;
                    zcache["session_data"][req.sessionID]["sa_file_path_conv"] = null;
                    zcache["session_data"][req.sessionID]["flag"] = null;
                    zcache["session_data"][req.sessionID]["false_upload"] = true;
                    zcache["session_data"][req.sessionID]["nodename"] = '';
                    zcache["session_data"][req.sessionID]["stdOut"] = '';
                    zcache["session_data"][req.sessionID]["stdOut_conv"] = '';
                } else {
                    zcache["uid_track"]++;
                    zcache["session_data"][req.sessionID] = {
                        "fields": [],
                        "argOfsar": '',
                        "uid": zcache["uid_track"],
                        "sa_file_path": null,
                        "sadf_type_det": null,
                        "sa_file_path_conv": null,
                        "flag": null,
                        "false_upload": true,
                        "nodename": '',
                        "stdOut": '',
                        "stdOut_conv": '',
                        "upload_dir_path": path.join(zcache["saDir"], zcache["uid_track"].toString())
                    };
                }
                callback(zcache["session_data"][req.sessionID]["upload_dir_path"]);
            }
        };

        self.routes['/'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.send(cache_get('index.html'));
        };
    };


    /**
     *  Initialize the server (express) and create the routes and register
     *  the handlers.
     */
    self.initializeServer = function() {
        self.createRoutes();

        self.app = express();

        var NOOP_FN = function () {
        };

        fs.mkdir(zcache["saDir"], function(error) {
            if (error) {
                util.log('mkdir() -- [' + zcache["saDir"] + '] : ' + error);
            }
        });

        self.app.use(session({
            store: new FileStore({
               logFn: NOOP_FN
            }),
            secret: 'keyboard cat',
            resave: true,
            saveUninitialized: true
          }));

        self.app.use('/static', express.static('static'));

        //  Add handlers for the app (from the routes).
        for (var r in self.routes) {
            if (r === '/upload') {
                self.app.post(r, self.routes[r]);
            } else {
                self.app.get(r, self.routes[r]);
            }
        }
    };


    /**
     *  Initializes the Sarjitsu application.
     */
    self.initialize = function() {
        self.setupVariables();
        populateCache();
        self.setupTerminationHandlers();

        // Create the express server and routes.
        self.initializeServer();


    };


    /**
     *  Start the server (starts up the Sarjitsu application).
     */
    self.start = function() {
        //  Start the app on the specific interface (and port).
        self.app.listen(self.port, self.ipaddress, function() {
            (function() {
                var childProcess = require("child_process");
                oldSpawn = childProcess.spawn;
                function mySpawn() {
                    // util.log('spawn() : [%s] %s',
                    //     arguments[0], arguments[1].join(' '));
                    var result = oldSpawn.apply(this, arguments);
                    return result;
                }
                childProcess.spawn = mySpawn;
            })();
            util.log('Node server started: ' + self.ipaddress + ':' + self.port);
        });
    };

};   /*  Sarjitsu Application.  */

/**
 *  main():  Main code.
 */
var zapp = new SarjitsuApp();
zapp.initialize();
zapp.start();
