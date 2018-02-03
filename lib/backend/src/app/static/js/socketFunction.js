 function socketConnection(data_new) {
    
     console.log(data_new);
    

     var socket = io.connect("http://" + document.domain + ':' + location.port + "/get_result");
     var sessionID = "{{data['sessionID']}}";
     var fileCount = "{{data['file_count']}}";
     var fileList = data["file_list"];

     var black_list = [];
     var file_count = 0;
     var search_key = ""
     console.log(black_list.length);
     console.log(fileList.length);

     socket.on('response', function(response_json) {
         if (response_json.is_processed) {
             var tbody = document.getElementById('results_table');

             // check if the property/key is defined in the object itself, not in parent
             // if (response_json.hasOwnProperty(key)) {           
            console.log(response_json)
             file_data = response_json;
             var tr = "<tr id=" + file_data.filename + ">";
             var filename;
             var status;
             if (file_data["if_valid"]) {
                 filename = "<span class='label label-success'>" + file_data.filename + "</span>";
                 status = "<span class='label label-primary'>Begin:</span>" + file_data.tstamp_beg + "<span class='label label-primary'>End:</span>" + file_data.tstamp_end;
             } else {
                 filename = "<span class='label label-danger'>" + file_data.filename + "</span>";
                 status = "<pre style='white-space:pre-wrap;''>" + "Invalid File" + '</pre>';
             }


             //     key, response_json[key];
             tr += "<td id=filename>" + filename + "</td>" + "<td id=systat >" + file_data.sadf_type_det + "</td>" + "<td id=hostname>" + file_data.nodename + "</td> + <td id=status>" + status + "</td></tr>";
             // }
             $("#results_table tbody").append(tr);

         }
     });
     while (black_list.length != fileList.length) {
         socket.on('connect', function() {
             // document.write(sessionID);

             search_key = "file_metadata:" + sessionID + ":" + fileList[file_count]
             if (black_list.indexOf(search_key) > -1) {
                 continue;
             } else {
                 socket.emit('get results', {
                     "search_key": search_key
                 });
             }



         });



     }
 }