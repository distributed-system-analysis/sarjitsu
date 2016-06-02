import os
import subprocess
import extract_sa

from app import app
from scripts.satools import oscode

def prepare(sessionID, target, sa_filename):
    file_metadata = "file_metadata:%s:%s" % (sessionID, sa_filename)
    SA_FILEPATH = app.cache.hget(file_metadata, "sadf_type_det")

    # CMD_VERSION = ['python3', 'scripts/satools/oscode', os.path.join(target, sa_filename)]
    # p1 = subprocess.Popen(CMD_VERSION, stdout=subprocess.PIPE, stderr)
    # TYPE = p1.communicate()[0]
    # app.logger.info("spawned..");

    # p2 = subprocess.Popen(["grep", "hda"], stdin=p1.stdout, stdout=subprocess.PIPE)
    # p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    # output = p2.communicate()[0]

    res = oscode.determine_version(file_path=SA_FILEPATH)
    if res(0):
        sadf_type_res = res(1)
        app.logger.info('sysstat version found for: %s' % sadf_type_res)
    else:
        sadf_type_res = "f23"
        app.logger.error(sadf_type_res)

        SA_FILEPATH_CONV = "%s_conv" % SA_FILEPATH
        CMD_CONVERT = ['LC_ALL=C', 'scripts/vos/analysis/bin/sadf-f23-64',
                        '-c', SA_FILEPATH]

        p2 = subprocess.Popen(CMD_CONVERT, stdout=open(SA_FILEPATH_CONV ,'w'),
                                stderr=subprocess.PIPE)
        err = p2.stderr
        if err:
            app.logger.error(err)
            return False

        sadf_type_res = p2.communicate()[0]
        app.logger.info('sysstat version was incompatible but dealt with')

        app.cache.hset(file_metadata, "sadf_type_det")
        app.cache.hset(file_metadata, "sa_file_path_conv")

        extract_sa.extract(sessionID, target, sa_filename)
