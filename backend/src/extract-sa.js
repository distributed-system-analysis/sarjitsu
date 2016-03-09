var output_line = '',
    result_ingestion = '',
    grep = require('simple-grep'),
    fs = require('fs'),
    grafana_endpoint='';

module.exports = {
    extract: function(req, res, _process, util, create, path, zcache, sa_file_path) {
        util.log("sadf type determined: " + zcache["session_data"][req.sessionID]["sadf_type_det"]);
        var commandObj,
            txtCmd = ['LC_ALL=C', 'scripts/vos/analysis/bin/sadf', '-x'];
        txtCmd[1] = txtCmd[1] + '-' + zcache["session_data"][req.sessionID]["sadf_type_det"] + '-' + '64';
        txtCmd.push(sa_file_path);
        txtCmd.push('--');
        var sar_file = path.join(zcache["session_data"][req.sessionID]["datafile_path"], "sar.xml");
        /* by default, extract all. This is because older versions of 'sadf' fail when certain
        orders of args are specified or when the data for arg is not present; the newer
        ones however fail silently and process rest of the args. The workaround includes
        generating all data with -A by default and then choosing the ones selected..
        (with exception handling ofcourse). */
        txtCmd.push('-A');
        util.log(txtCmd.join(' '));
        commandObj = _process.spawn('env', txtCmd);
        util.log("spawned..");

        commandObj.stdout.on('data', function (data) {
            zcache["session_data"][req.sessionID]["stdOut"] += data.toString();
        });
        commandObj.stdout.on('end', function () {

            var nodename_cmd = 'scripts/detect_nodename ' + sar_file;
            var sar_cmd = function() {
                var nodenameObj = _process.spawn('env', nodename_cmd.split(' '));
                nodenameObj.stdout.on('data', function (data) {
                    zcache["session_data"][req.sessionID]["nodename"] += data.toString();
                });
                nodenameObj.stdout.on('end', function(){
                    var ix_res = {};
                    var sarObj, sarCmd = ['scripts/vos/analysis/bin/index-sar',
                                          sar_file,
                                          zcache["session_data"][req.sessionID]["nodename"]];
                    util.log('ES indexing cmd: ' + sarCmd.join(' '));
                    sarObj = _process.spawn('env', sarCmd);
                    sarObj.stdout.on('data', function (data) {
                        output_line = data.toString();
                        match_result = output_line.match(/(grafana_range_begin|grafana_range_end) \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/g);
                        if(match_result) {
                            for(var i=0; i<match_result.length; i++) {
                                match_result[i] = match_result[i].split(' ');
                                ix_res[match_result[i][0]] = match_result[i][1];
                            }
                        } else {
                            result_ingestion += output_line;
                        }
                    });
                    sarObj.stdout.on('end', function(){
                        util.log("beg: " + ix_res['grafana_range_begin']);
                        util.log("end: " + ix_res['grafana_range_end']);

                        create.dashboard(_process, util, zcache["session_data"][req.sessionID]["nodename"],
                            zcache["session_data"][req.sessionID]["fields"],
                            ix_res['grafana_range_begin'],
                            ix_res['grafana_range_end']);
                    });
                    sarObj.stderr.on('data', function (data) {
                        util.log('stderr: ' + data);
                    });
                    sarObj.stdout.on('close', function(){
                        util.log('[ES data ingested] -- ' + zcache["session_data"][req.sessionID]["nodename"]);
                        if (!!zcache["session_data"][req.sessionID]["nodename"]) {
                            // res.write("<br/><br/><b>Output</b><br/><pre>");
                            // res.write(result_ingestion);
                            function callback(ff){
                              grep('dashboard_url', '/etc/sar-index.cfg', function(list){
                                var _tmp = list[0].results[0];
                                var line = _tmp.line_number + ":" + _tmp.line;
                                grafana_endpoint = line.split('dashboard_url=')[1];
                                // console.log('inside: ' + grafana_endpoint);
                                ff();
                              });
                            };

                            callback(function(){
                              res.write("Success! <u>Nodename: <b>" +
                                        zcache["session_data"][req.sessionID]["nodename"] + "</b></u>");
                              res.write("<p>kindly go to <a href='" + grafana_endpoint +
                                        "'>this Grafana instance</a> and login with <pre>admin/admin</pre>" +
                                        " to find content for your nodename result..</p>");
                              // console.log('outside: ' + grafana_endpoint);
                              res.end();
                            });
                        } else {
                            res.write("Fail");
                            res.end();
                        }
                        output_line = '';
                        result_ingestion = '';
                    });
                });
                nodenameObj.stderr.on('data', function (data) {
                    util.log('stderr: ' + data);
                    output_line = '';
                    result_ingestion = '';
                });
            };

            fs.writeFile(sar_file, zcache["session_data"][req.sessionID]["stdOut"], { flags: 'w', encoding: 'utf-8' }, function(err) {
                if(err) {
                    util.log("SAR data extraction *failed*!");
                    return util.log(err);
                } else {
                    util.log("SAR data extraction *completed*!");
                    sar_cmd();
                }
            });

        });
        commandObj.stderr.on('data', function (data) {
            util.log('stderr: ' + data.toString());
            res.write('Sorry : ' + data.toString());
            res.end();
        });

        commandObj.on('close', function (code) {
            zcache["session_data"][req.sessionID]["sadf_type_det"] = '';
            util.log('child process exited with code ' + code);
        });
    }
}
