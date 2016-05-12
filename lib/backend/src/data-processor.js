var sa_processor = require('./extract-sa.js'),
    fs = require('fs');

module.exports = {
    prepare: function(req, res, _process, util, create, path, zcache) {

        // BEGIN: automatic oscode detection
        var cmd_obj,
            determine_sa_cmd = ['scripts/satools/oscode', zcache["session_data"][req.sessionID]["sa_file_path"]];

        util.log(determine_sa_cmd.join(' '));
        cmd_obj = _process.spawn('python3', determine_sa_cmd);

        // process spawned command output
        cmd_obj.stdout.on('data', function (data) {
            zcache["session_data"][req.sessionID]["sadf_type_det"] = data.toString().split('\n')[0];
        });

        cmd_obj.stdout.on('end', function (next) {
            res.writeHead(200, { 'Content-Type' : 'text/html;charset=utf-8'});

            if(!zcache["session_data"][req.sessionID]["sadf_type_det"]) {
                zcache["session_data"][req.sessionID]["sadf_type_det"] = "f23";
                var convertObj, 
                    convertCmd = ['LC_ALL=C', 'scripts/vos/analysis/bin/sadf-f23-64', '-c', 
                                    zcache["session_data"][req.sessionID]["sa_file_path"]];

                zcache["session_data"][req.sessionID]["sa_file_path_conv"] = zcache["session_data"][req.sessionID]["sa_file_path"] + "_conv";
                convertObj = _process.spawn('env', convertCmd);
                util.log("spawned convertor..");
                util.log(convertCmd);
                var wstream = fs.createWriteStream(zcache["session_data"][req.sessionID]["sa_file_path_conv"]);
                convertObj.stdout.on('data', function (data) {
                    wstream.write(data);
                }); 

                convertObj.stdout.on('end', function () {});

                convertObj.stderr.on('data', function (data) {
                    util.log('stderr: ' + data);
                });

                convertObj.stdout.on('close', function(){
                    util.log('sysstat version was incompatible but dealt with');
                    sa_processor.extract(req, res, _process, util, create, path, zcache, 
                                        zcache["session_data"][req.sessionID]["sa_file_path_conv"]);
                });
            } else {
                util.log('sysstat version was compatible');
                sa_processor.extract(req, res, _process, util, create, path, zcache, 
                    zcache["session_data"][req.sessionID]["sa_file_path"]);
            } 
        });

        cmd_obj.stdout.on('close', function(){});

        cmd_obj.stderr.on('data', function (data) {
          util.log("stderr on 'data': " + data);
        });
    }
}
