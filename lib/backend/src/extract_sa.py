import os
import requests
import subprocess
import creation
from app import app

def extract(sessionID, target, sa_filename, TSTAMPS={}):
    CMD_CONVERT = ['LC_ALL=C', '-x', "--", "-A"]
    SAR_XML_FILEPATH = os.path.join(target, "%s.%s" % (sa_filename, "sar.xml"))
    file_metadata = "file_metadata:%s:%s" % (sessionID, sa_filename)

    sadf_type_det = app.cache.hget(file_metadata, "sadf_type_det")
    app.logger.info("sadf type determined: %s" % sadf_type_det)

    _SCRIPT = "%s-%s-64" % ('scripts/vos/analysis/bin/sadf', sadf_type_det)
    CMD_CONVERT.insert(1, _SCRIPT)

    conv_path = app.cache.hget(file_metadata, "sa_file_path_conv")
    if conv_path:
        target_file = conv_path
    else:
        target_file = app.cache.hget(file_metadata, "sa_file_path")

    CMD_CONVERT.insert(-2, target_file)

    p1 = subprocess.Popen(CMD_CONVERT, stdout=open(SAR_XML_FILEPATH, 'w'))
    app.logger.info("spawned..");

    # p2 = subprocess.Popen(["grep", "hda"], stdin=p1.stdout, stdout=subprocess.PIPE)
    # p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    # output = p2.communicate()[0]

    CMD_GREP = ["scripts/detect_nodename", SAR_XML_FILEPATH]
    p2 = subprocess.Popen(CMD_GREP, stdout=subprocess.PIPE)
    NODENAME = p2.communicate()[0]

    CMD_INDEXING = ['scripts/vos/analysis/bin/index-sar',
                    SAR_XML_FILEPATH, NODENAME]
    app.logger.info('ES indexing cmd: ' + " ".join(CMD_INDEXING))
    p3 = subprocess.Popen(CMD_INDEXING, stdout=subprocess.PIPE)

    app.logger.info("[ES data ingested] -- %s" % NODENAME);

    RESULT_RAW = p3.communicate()[0].splitlines()
    TMP = [line for line in RESULT_RAW if line.startswith('grafana_range')]
    for line in TMP:
        k,v = line.split(' ')
        TSTAMPS[k] = v

    app.logger.info('beg: %s' % TSTAMPS['grafana_range_begin'])
    app.logger.info('end: %s' % TSTAMPS['grafana_range_end'])

    GRAPHING_OPTIONS = app.cache.hget("sar_args:%s" % sessionID, "fields")
    creation.dashboard(NODENAME, GRAPHING_OPTIONS,
                        TSTAMPS['grafana_range_begin'],
                        TSTAMPS['grafana_range_end'])

    return (NODENAME, TSTAMPS)
