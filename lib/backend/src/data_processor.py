import os
import subprocess
import extract_sa

from app import app
from scripts.satools import oscode

def prepare(sessionID, target, sa_filename):
    file_metadata = "file_metadata:%s:%s" % (sessionID, sa_filename)
    SA_FILEPATH = os.path.join(target, sa_filename)
    res = oscode.determine_version(file_path=SA_FILEPATH)
    if res[0]:
        sadf_type_res = res[1]
        app.logger.info('sysstat version found for: %s' % sadf_type_res)
        app.cache.hset(file_metadata, "sa_file_path", SA_FILEPATH)
    else:
        sadf_type_res = "f23"
        app.logger.error(sadf_type_res)

        SA_FILEPATH_CONV = "%s_conv" % SA_FILEPATH
        CMD_CONVERT = ['scripts/vos/analysis/bin/sadf-f23-64',
                        '-c', SA_FILEPATH]

        p2 = subprocess.Popen(CMD_CONVERT, stdout=open(SA_FILEPATH_CONV ,'w'),
                                stderr=subprocess.PIPE, env={'LC_ALL': 'C'})
        err = p2.stderr
        if err:
            app.logger.error(err)
            return False

        sadf_type_res = p2.communicate()[0].decode().replace("\n", "")
        app.logger.info('sysstat version was incompatible but dealt with')
        app.cache.hset(file_metadata, "sa_file_path_conv", SA_FILEPATH_CONV)

    app.cache.hset(file_metadata, "sadf_type_det", sadf_type_res)
    #FIXME: handle exceptons
    return extract_sa.extract(sessionID, target, sa_filename)
