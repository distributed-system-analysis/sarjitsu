var request = require('request'),
	exec = require('child_process').exec;

// grep = require('simple-grep');
// simple-grep ^0.0.1 can't be located anymore for some reason.
// below code is from https://github.com/gawkermedia/simple-grep
var grep = function(what, where, callback){

	exec("grep " + what + " " + where + " -nr", function(err, stdin, stdout){
		var list = {}

		var results = stdin.split('\n');

	    // remove last element (it’s an empty line)
	    results.pop();
	    for (var i = 0; i < results.length; i++) {
	    	var eachPart = results[i].split(':') //file:linenum:line
	    	list[eachPart[0]] = []
	    }
	    for (var i = 0; i < results.length; i++) {
	    	var eachPart = results[i].split(':') //file:linenum:line
	    	var details = {}
	    	var filename = eachPart[0]
	    	details['line_number'] = eachPart[1]

	    	eachPart.shift()
	    	eachPart.shift()
	    	details['line'] = eachPart.join(':')

	    	list[filename].push(details)
	    }


	    var results = []
	    var files = Object.keys(list)
	    for(var i = 0; i < files.length; i++){
	    	results.push({'file' : files[i], 'results' : list[files[i]]})
	    }

	    callback(results)
	});
}

module.exports = {
    dashboard: function (_process, util, hostname, sar_params, ts_begin, ts_end) {
        grep('api_url', '/etc/sar-index.cfg', function(list){
          var _tmp = list[0].results[0];
          var line = _tmp.line_number + ":" + _tmp.line;
          var api_endpoint = line.split('api_url = ')[1];
          console.log(api_endpoint);
          console.log(ts_begin + " : " + ts_end + " : " + hostname + " : " + sar_params);

          request.post(api_endpoint,
            { json: {
                  ts_beg: ts_begin,
                  ts_end: ts_end,
                  nodename: hostname.replace(/\n/g, ''),
                  modes: sar_params.join(',')
                }
            },
            function (error, response, body) {
							if (!response.hasOwnProperty('statusCode')) {
								util.log("no reponse.statusCode received from dashboard creation engine");
								util.log(JSON.stringify(response));
							} else if (!error && response.statusCode == 200) {
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
