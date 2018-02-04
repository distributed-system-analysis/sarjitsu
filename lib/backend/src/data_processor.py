import os
import subprocess
import extract_sa
from celery.contrib import rdb
from app import app
from scripts.satools import oscode

def prepare(sessionID, target, sa_filename):
    meta_data = {
        "sa_file_path": '',
        "sa_file_path_conv": '',
        "if_valid": False,
        "is_processed": False,
        "sadf_type_det": '',
        "tstamps_beg": '',
        "tstamps_end": '',
        "nodename": ''
    }
    file_metadata = "file_metadata:%s:%s" % (sessionID, sa_filename)
    SA_FILEPATH = os.path.join(target, sa_filename)
    res = oscode.determine_version(file_path=SA_FILEPATH)
    if res[0]:

        meta_data["sa_file_path"] = SA_FILEPATH
        meta_data["sa_file_path_conv"] = ''
        meta_data["if_valid"] = True
        meta_data["sadf_type_det"] = res[1]
        
    else:
        app.logger.warn("couldn't determine sysstat version for file..")
        SA_FILEPATH_CONV = "%s_conv" % SA_FILEPATH
        CMD_CONVERT = ['scripts/vos/analysis/bin/sadf-f23-64',
                        '-c', SA_FILEPATH]

        p2 = subprocess.Popen(CMD_CONVERT, stdout=open(SA_FILEPATH_CONV ,'w'),
                                stderr=subprocess.PIPE, env={'LC_ALL': 'C'})
        p2.wait()
        err = p2.stderr
        if err:
            err = err.read().decode()
            app.logger.error(err)
            if "Invalid" in err:
                app.logger.error("SAR data extraction *failed*!")
                q[sa_filename] = (None, "Invalid", None)
                meta_data["sa_file_path"] = SA_FILEPATH
                meta_data["sa_file_path_conv"] = SA_FILEPATH_CONV
                meta_data["is_processed"] = True

                app.cache.hmset(file_metadata, meta_data)
                return

        sadf_type_res = "f23"
        _tmp = p2.communicate()[0]
        app.logger.warn(_tmp)

        # rdb.set_trace()
        app.logger.info('sysstat version was incompatible but dealt with')
        meta_data["sa_file_path"] = SA_FILEPATH
        meta_data["sa_file_path_conv"] = SA_FILEPATH_CONV
        meta_data["if_valid"] = True
        meta_data["sadf_type_det"] = sadf_type_res

    app.cache.hmset(file_metadata, meta_data)
 
    extract_sa.extract(sessionID, target, sa_filename, file_metadata)
    app.cache.hset(file_metadata, "is_processed", True)
    return 


# def post_prepare(filename, **q_list):
#     nodename, meta, sadf = q_list[filename]
#     result = [filename, sadf, nodename, meta]
#     if not meta:
#         #FIXME: on failure, delete all uploaded files
#         result.insert(0, False)
#         # add message in meta
#         result[-1] = "ES Indexing Failed"
#     elif meta == "Invalid":
#         #FIXME: on failure, delete all uploaded files
#         result.insert(0, False)
#         # add message in meta
#         result[-1] = "Invalid Input"
#     else:
#         _valid_results_found = True
#         result.insert(0, True)
#     # print("***********************",result)
#     return result
        


