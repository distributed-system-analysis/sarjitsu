var request = require('request'),
    grep = require('simple-grep');

module.exports = {
    dashboard: function (_process, util, hostname, sar_params, ts_begin, ts_end) {
        // var grafanaObj, grafanaCmd = ['/src/scripts/create_dashboard',
        //                             '-b', ts_begin, '-e', ts_end,
        //                             '-n', hostname.replace(/\n/g, ''), '-m',
        //                             sar_params.join(' ')];
        // util.log(grafanaCmd.join(' '));
        // grafanaObj = _process.spawn('env', grafanaCmd);
        // grafanaObj.stdout.on('data', function (data) {
        //     util.log(data.toString());
        // });
        // grafanaObj.stdout.on('end', function(){});
        // grafanaObj.stderr.on('data', function (data) {
        //   util.log('stderr: ' + data);
        // });
        // grafanaObj.stdout.on('close', function(){});
        grep('api_url', '/etc/sar-index.cfg', function(list){
          var _tmp = list[0].results[0];
          var line = _tmp.line_number + ":" + _tmp.line;
          var api_endpoint = line.split('api_url = ')[1];

          request.post(api_endpoint,
            { json: {
                  ts_beg: ts_begin,
                  ts_end: ts_end,
                  nodename: hostname.replace(/\n/g, ''),
                  modes: sar_params.join(',')
                }
            },
            function (error, response, body) {
              if (!error && response.statusCode == 200) {
                util.log(JSON.stringify(body));
              }
              else {
                util.log("status: " + response.statusCode);
                util.log("error: \n" + error);
                util.log("body: \n" + JSON.stringify(body));
              }
          });
        });
    }
}
