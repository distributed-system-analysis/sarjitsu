import os
import creation
import data_processor
from app import app, sar_modes
from celery import group
from datetime import datetime
from threading  import Thread
from tasks import file_processor
from uuid import uuid4
from werkzeug import secure_filename

SINGLE_MODE = list(enumerate(sar_modes['single'], start=1))
MULTI_MODE = list(enumerate(sar_modes['multiple'], start=1))

def update_cache(sessionID, flag=True, args='A'):
    if flag:
        params = ','.join(list(sar_modes['single'].keys()))
        arg_data = {
            'argOfsar': args,
            'fields': params
        }
    else:
        field_values = dict(enumerate(sar_modes['single'], start=1))
        arg_data = {
            'argOfsar': args,
            'fields': ','.join([field_values[i] for i in args])
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

def upload_files(target, sessionID, datafiles):
    """Upload the files to the server directory

    Keyword arguments:
    target - The target directory to upload the files to
    sessionID - The user session ID
    datafiles - The list of the files to be uploaded

    Returns:
        List
    """

    filename_list = []
    for datafile in datafiles:
        filename = secure_filename(datafile.filename).rsplit("/")[0]
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename += "_%s_%s" %(uuid4().hex, current_time) 
        update_file_metadata(sessionID, filename)
        filename_list.append(filename)
        destination = os.path.join(target, filename)
        app.logger.info("Accepting incoming file: %s" % filename)
        app.logger.info("Saving it to %s" % destination)
        datafile.save(destination)
    return filename_list

def begin(target, sessionID, form):

    if form.data['check_all']:
        update_cache(sessionID, flag=True, args='A')
    else:
        _tmp = form.data['graph_types']
        update_cache(sessionID, flag=False, args=_tmp)

    os.makedirs(target, exist_ok=True)

    filename_list = upload_files(target, sessionID, form.datafile)
    
    app.cache.set("filenames:%s" % sessionID, filename_list)
    t_list  = []
    q_list = dict.fromkeys(filename_list)
    celery_res = group(file_processor.s(sessionID, target, fname) for fname in filename_list)()

    return filename_list
