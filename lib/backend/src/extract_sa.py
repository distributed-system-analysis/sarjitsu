import os
import requests
import subprocess
import creation
from app import app
from scripts.vos.analysis.lib import index_sar

def extract(sessionID, target, sa_filename):
    TSTAMPS={}
    CMD_CONVERT = ['-x', "--", "-A"]
    SAR_XML_FILEPATH = os.path.join(target, "%s.%s" % (sa_filename, "sar.xml"))
    file_metadata = "file_metadata:%s:%s" % (sessionID, sa_filename)

    sadf_type_det = app.cache.hget(file_metadata, "sadf_type_det").decode()
    app.logger.info("sadf type determined: %s" % sadf_type_det)

    _SCRIPT = "%s-%s-64" % ('scripts/vos/analysis/bin/sadf', sadf_type_det)
    CMD_CONVERT.insert(0, _SCRIPT)

    conv_path = app.cache.hget(file_metadata, "sa_file_path_conv")
    if conv_path:
        target_file = conv_path.decode()
    else:
        target_file = app.cache.hget(file_metadata, "sa_file_path").decode()

    CMD_CONVERT.insert(-2, target_file)

    #FIXME: check if env in Popen is working fine
    p1 = subprocess.Popen(CMD_CONVERT, env={'LC_ALL': 'C'},
                            stdout=open(SAR_XML_FILEPATH, 'w'))
    app.logger.info("spawned..");

    CMD_GREP = ["scripts/detect_nodename", SAR_XML_FILEPATH]
    p2 = subprocess.Popen(CMD_GREP, stdout=subprocess.PIPE)
    NODENAME = p2.communicate()[0].decode().replace("\n", "")

    # import pdb; pdb.set_trace()
    #FIXME: check if call_indexer works everytime. And if it handles errors
    try:
        #FIXME: bad XML ExpatError
        raise
        state, beg, end = index_sar.call_indexer(file_path=SAR_XML_FILEPATH,
                               _nodename=NODENAME,
                               cfg_name=app.config.get('CFG_PATH'),
                               run_unique_id=sessionID,
                               run_md5=sessionID)
        if state:
            TSTAMPS['grafana_range_begin'] = beg
            TSTAMPS['grafana_range_end'] = end
    except Exception as E:
        #FIXME: remove if we use the try: approach in future.
        app.logger.warn("=====Running alternate ES indexing script======")
        app.logger.warn(E)
        CMD_INDEXING = ['scripts/vos/analysis/bin/index-sar',
                        SAR_XML_FILEPATH, NODENAME]
        app.logger.info('ES indexing cmd: ' + " ".join(CMD_INDEXING))
        p3 = subprocess.Popen(CMD_INDEXING, stdout=subprocess.PIPE)
        RESULT_RAW = p3.communicate()[0].decode().splitlines()
        TMP = [line for line in RESULT_RAW if line.startswith('grafana_range')]
        if TMP:
            for line in TMP:
                k,v = line.split(' ')
                TSTAMPS[k] = v

    if TSTAMPS:
        app.logger.info("[ES data ingested] -- %s" % NODENAME);
        app.logger.info('beg: %s' % TSTAMPS['grafana_range_begin'])
        app.logger.info('end: %s' % TSTAMPS['grafana_range_end'])

        GRAPHING_OPTIONS = app.cache.hget("sar_args:%s" % sessionID, "fields").decode()
        creation.dashboard(NODENAME, GRAPHING_OPTIONS, TSTAMPS)

        return (NODENAME, TSTAMPS, sadf_type_det)
    else:
        return (NODENAME, "Elasticsearch Indexing Failed", sadf_type_det)
