import os
import creation
import data_processor
from app import app, sar_modes
from threading  import Thread
from werkzeug import secure_filename

SINGLE_MODE = list(enumerate(sar_modes['single'], start=1))
MULTI_MODE = list(enumerate(sar_modes['multiple'], start=1))

def update_cache(sessionID, flag=True, args='A'):
    #FIXME
    params = ','.join(list(sar_modes['single'].keys()))
    if flag:
        arg_data = {
            'argOfsar': args,
            'fields': params
        }
    else:
        arg_data = {
            'argOfsar': 'A',
            'fields': params
        }
    app.cache.hmset("sar_args:%s" % sessionID, arg_data)

def update_file_metadata(sessionID, safile):
    file_metadata = {
          "filename": safile,
          "sadf_type_det": "",
          "sa_file_path_conv": "",
          "nodename": ''
    }
    app.cache.hmset("file_metadata:%s:%s" %
                        (sessionID, safile), file_metadata)

def begin(target, sessionID, form):

    #FIXME: not using check_all and empty graph_types triggers error
    if form.data['check_all']:
        update_cache(sessionID, flag=True, args='A')
    else:
        _tmp = form.data['graph_types']
        update_cache(sessionID, flag=False, args=_tmp)

    os.makedirs(target, exist_ok=True)

    filename_list = []
    for upload in form.datafile:
        filename = secure_filename(upload.filename).rsplit("/")[0]
        update_file_metadata(sessionID, filename)
        filename_list.append(filename)
        destination = os.path.join(target, filename)
        app.logger.info("Accepting incoming file: %s" % filename)
        app.logger.info("Saving it to: %s" % destination)
        upload.save(destination)

    app.cache.set("filenames:%s" % sessionID, filename_list)
    response = {"nodenames_info": []}

    #FIXME: single file upload error: None timestamp (fix for threading.....
    #FIXME: ......wait for file upload, add timeouts to Popen, check close_fds)
    #FIXME: multifile upload not working

    t_list  = []
    q = dict.fromkeys(filename_list)

    for i in range(len(filename_list)):
        t = Thread(target=data_processor.prepare, daemon=True,
                args=(sessionID, target, filename_list[i], q))
        t_list.append(t)

    for j in t_list:
        j.start()

    for j in t_list:
        j.join()

    _valid_results_found = False
    for filename in filename_list:
        nodename, meta, sadf = q[filename]
        result = [filename, sadf, nodename, meta]
        if not meta:
            #We have a failure here, let's delete the uploaded files
            try:
                remove_target = os.path.join(target, filename)
                os.remove(remove_target)
            except OSError:
                app.logger.info("Unable to delete %s" % remove_target)	
            result.insert(0, False)
            # add message in meta
            result[-1] = "ES Indexing Failed"
        elif meta == "Invalid":
            #Delete the files if there is an error
            try:
                remove_target = os.path.join(target, filename)
                os.remove(remove_target)
            except OSError:
                app.logger.info("Unable to delete %s" % remove_target)
            result.insert(0, False)
            # add message in meta
            result[-1] = "Invalid Input"
        else:
            _valid_results_found = True
            result.insert(0, True)
        response["nodenames_info"].append(result)

    #FIXME
    return (_valid_results_found, response)
