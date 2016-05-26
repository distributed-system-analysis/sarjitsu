var sa_processor = require('./extract-sa.js'),
    fs = require('fs');

module.exports = {
    prepare: function(req, res, _process, util, create, path, zcache, counter) {
        var current_sa_fp = zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sa_file_path"];
        // BEGIN: automatic oscode detection
        var cmd_obj,
        determine_sa_cmd = ['scripts/satools/oscode', current_sa_fp];

        util.log(determine_sa_cmd.join(' '));
        cmd_obj = _process.spawn('python3', determine_sa_cmd);

        // process spawned command output
        cmd_obj.stdout.on('data', function (data) {
          zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sadf_type_det"] = data.toString().split('\n')[0];
        });

        cmd_obj.stdout.on('end', function (next) {

          if(!zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sadf_type_det"]) {
            zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sadf_type_det"] = "f23";
            var convertObj,
            convertCmd = ['LC_ALL=C', 'scripts/vos/analysis/bin/sadf-f23-64', '-c',
            current_sa_fp];

            zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sa_file_path_conv"] = current_sa_fp + "_conv";
            convertObj = _process.spawn('env', convertCmd);
            util.log("spawned convertor..");
            util.log(convertCmd);
            var wstream = fs.createWriteStream(zcache["session_data"][req.sessionID]["file_ops_blob"][counter]["sa_file_path_conv"]);
            convertObj.stdout.on('data', function (data) {
              wstream.write(data);
            });

            convertObj.stdout.on('end', function () {});

            convertObj.stderr.on('data', function (data) {
              util.log('stderr: ' + data);
            });

            convertObj.stdout.on('close', function(){
              util.log('sysstat version was incompatible but dealt with');
            });
          } else {
            util.log('sysstat version was compatible');
          }
          sa_processor.extract(req, res, _process, util, create, path, zcache, counter);

        });

        cmd_obj.stdout.on('close', function(){});

        cmd_obj.stderr.on('data', function (data) {
          util.log("stderr on 'data': " + data);
        });

  }
}
