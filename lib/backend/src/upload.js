var fs = require('fs'),
    path = require('path'),
    Busboy = require('busboy'),
    processor = require('./data-processor.js'),
    modes_path = path.resolve(__dirname, 'static/sar_args_mapping.json'),
    modes = JSON.parse(fs.readFileSync(modes_path)).single;

// TODO: .. get cpu 0/1/2... input from user, if user wants
//          to provide  a specific cpu input

module.exports = {
    begin: function(req, res, next, _process, util, create, zcache) {
        var busboy = new Busboy({ headers: req.headers, immediate: true });

        busboy.on('field', function(fieldname, val) {

            if (fieldname == 'check_all') {
                zcache["session_data"][req.sessionID]["argOfsar"] = 'A';
                zcache["session_data"][req.sessionID]["fields"] = Object.keys(modes);
                zcache["session_data"][req.sessionID]["flag"] = 1;
            } else if (fieldname == 'graph_types') {
                if (!zcache["session_data"][req.sessionID]["flag"]) {
                    zcache["session_data"][req.sessionID]["argOfsar"] = zcache["session_data"][req.sessionID]["argOfsar"].concat(modes[val]);
                    zcache["session_data"][req.sessionID]["fields"].push(val);
                }
            }
        });

        busboy.on('file', function(fieldname, file, filename, encoding, mimetype) {
            // path hierarcy is as follows: <saDir>/<sessionID>/<userID>/<sar_file>/
            util.log("File received.");
            zcache["session_data"][req.sessionID]["false_upload"] = false;
            zcache["session_data"][req.sessionID]["file_ops_counter"]++;
            var counter = zcache["session_data"][req.sessionID]["file_ops_counter"];
            datafile_path = path.join(zcache["session_data"][req.sessionID]["upload_dir_path"], JSON.stringify(counter));

            zcache["session_data"][req.sessionID]["file_ops_blob"][counter] = {
              "datafile_path": datafile_path,
              "sa_file_path": path.join(datafile_path, path.basename(filename)),
              "sadf_type_det": null,
              "sa_file_path_conv": null,
              "nodename": ''
            };

            fs.mkdir(datafile_path, function(error) {
              if (error) {
                util.log('mkdir() -- [' + datafile_path + '] : ' + error);
              }
            });

            write_file(function(){
              var path_track_new = zcache["session_data"][req.sessionID]["uid"].toString() + '/' + filename + '/';
              if (req.session.paths) {
                if (req.session.paths.indexOf(path_track_new) === -1) {
                  req.session.paths.push(path_track_new)
                }
              } else {
                req.session.paths = [path_track_new];
              }
            });

            function write_file(callback) {
              file.pipe(fs.createWriteStream(zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sa_file_path"]));
              util.log("[Uploaded] " + zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sa_file_path"]);
              callback();
            }
        });

        busboy.on('finish', function() {
            if(zcache["session_data"][req.sessionID]["fields"].length != 0 && zcache["session_data"][req.sessionID]["false_upload"] === false){
              res.writeHead(200, { 'Content-Type' : 'text/html;charset=utf-8'});
              // res.write("uploading.. kindly wait..");
              for (var counter=1; counter <= zcache["session_data"][req.sessionID]["file_ops_counter"]; counter++) {
                processor.prepare(req, res, _process, util, create, path, zcache, counter);
              }
              // res.end();
            } else {
                res.writeHead(200, { 'Content-Type' : 'text/html;charset=utf-8'});
                res.write("Kindly specify an activity to be visualized / file to be uploaded..");
                res.write("Either use <pre>check_all</pre> or select multiple choices from the list.");
                res.end();
            }
        });
        return req.pipe(busboy);
    }
}
