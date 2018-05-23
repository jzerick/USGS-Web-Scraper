from search import *
from cloudstoragedriver import Cloud

import signal
import sys
import daemon
import os
import time
import argparse
import socket
import threading
import lace, logging
import subprocess
from functools import reduce

import libdlt
from unis.runtime import Runtime

UNIS_URL="http://localhost:8888"
LOCAL_UNIS_HOST="localhost"
LOCAL_UNIS_PORT=9000

# for reference
EXNODE_SCHEMA_URL="http://unis.crest.iu.edu/schema/exnode/6/exnode#"

def download_recent_USGS_TIFFS(n,exnodes_present,coordinates):
    '''
        Queries google for the last week of TIFFS uploaded from USGS.

        Downloads them to your file system based on the path laid out by Google.

    '''
    if coordinates != None:
        coordinates = parse_coordinates(coordinates)

    # fetch locations of TIFFS uploaded in the last week
    q = Query(log)
    m_url2metadata = q.find_n_days_old(n,coordinates)

    log.info('%d file(s) to be downloaded.' % len(m_url2metadata))

    # Instantiate the web scraper to find urls in each bucket.
    # This is a dummy email I don't care about uploading to git, too lazy to make an encrypted config file atm.
    # dont use above, just filler for if the web scraper ever becomes a thing again

    C = Cloud(log,path = '/data')
    m_url2files_to_upload = {}

    scene_count = 0
    # for each bucket, get the relevant urls and download them.
    for url in m_url2metadata:
        scene_count += 1
        log.info('Working on %s of %s Buckets.' % (scene_count, len(m_url2metadata)))
        log.info('-> now fetching Bucket: %s' % url)

        m_url2files_to_upload[url] = C.DownloadBucket(url,exnodes_present)

        if KILL_SWITCH > 0 and scene_count >= KILL_SWITCH:
            log.info('- KILL SWITCH ENGAGED -')
            break

    log.info('%s scene(s) added.' % scene_count)

    return m_url2metadata,m_url2files_to_upload

def coordinates_valid(coordinates):
    if coordinates == None:
        return True
        
    try:
        latitude,longitude = map(lambda x: float(x),coordinates.split(','))
    except:
        return False
    
    # check coordinates' validity
    if -90 <= latitude and latitude <= 90 and -180 <= longitude and longitude <= 180:
        return True

    return False

def parse_coordinates(coordinates):
    C = coordinates.split(',')
    return (float(C[0]), float(C[1]))

def add_metadata(exn,M,fn):
    exn.name = fn

    # pulled from Google Cloud 
    exn.properties.scene_id = M['scene_id']
    exn.properties.product_id = M['product_id']
    exn.properties.spacecraft_id = M['spacecraft_id']
    exn.properties.sensor_id = M['sensor_id'] 
    exn.properties.date_acquired = M['date_acquired'] 
    exn.properties.sensing_time = M['sensing_time'] 
    exn.properties.collection_number = M['collection_number'] 
    exn.properties.collection_category = M['collection_category'] 
    exn.properties.data_type = M['data_type'] 
    exn.properties.wrs_path = M['wrs_path'] 
    exn.properties.wrs_row = M['wrs_row'] 
    exn.properties.cloud_cover = M['cloud_cover'] 
    exn.properties.north_lat = M['north_lat'] 
    exn.properties.south_lat = M['south_lat'] 
    exn.properties.west_lon = M['west_lon'] 
    exn.properties.east_lon = M['east_lon'] 
    exn.properties.total_size = M['total_size'] 
    exn.properties.base_url = M['base_url']

    # alternatively, use the file structure
    # /[SENSOR_ID]/PRE/[PATH]/[ROW]/[SCENE_ID]/
    S = fn.split('/')
    sensor_id = S[0]
    wrs_path = int(S[2])
    wrs_row = int(S[3])
    scene_id = S[4]

    # here, could extract data from GEOTIFF

    # remove the file extension, then get the pathless filename
    T = (fn.split('.')[0]).split('/')[-1]

    # and get the remaining bits of encoded metadata after the _RT_
    RT_code = T.split('_RT_')[-1]
    exn.properties.rt_code = RT_code

    # get the approximate center for ease of visualization
    exn.properties.center_lat = (exn.properties.north_lat + exn.properties.south_lat)/2.
    exn.properties.center_long = (exn.properties.west_lon + exn.properties.east_lon)/2.

def shutdown(signum, frame):  # signum and frame are mandatory
    sys.exit(0)

def get_script_dir():
    fn_path = os.path.abspath(__file__)
    return reduce(lambda x,y: x+'/'+y, fn_path.split('/')[:-1]) 

def main():
    global DOWNLOAD_DIR, KILL_SWITCH, log

    log = lace.logging.getLogger("landsat_retriever")
    log.setLevel(logging.INFO)

    # borrowed from the EODN Harvester, 
    # https://github.com/datalogistics/eodn-harvester/blob/master/eodnharvester/app.py
    # and the WildfireDLN dln_ferry,
    # https://github.com/datalogistics/wildfire-dln/blob/master/ferry/dln_ferry.py
    parser = argparse.ArgumentParser(description = "Harvest Landsat 7/8 data for WildfireDLN")
    parser.add_argument('-w', '--download', type=str, default='./data',
        help = 'Set local download directory')
        
    parser.add_argument('-n', '--ndays', type=int, default=7,
        help = "Retrieve only images captured in the last n days (default is n=7)")
        
    parser.add_argument('-k', '--killswitch', type=int, default=-1,
        help = "Enable and activate kill switch after retrieving k buckets (default is disabled)")
        
    parser.add_argument('-c', '--coordinates', type=str, default=None,
        help = "Retrieve only images containing the specified coordinates as latitude,longitude, e.g. -c-8.0,137.0")
        
    parser.add_argument('-d', '--daemon', action = 'store_true', 
        help = "Indicates that the process should be run as a daemon")
        
    parser.add_argument('-v', '--verbose', action='store_true',
        help = 'Produce verbose output from the script')
        
    parser.add_argument('-q', '--quiet', action='store_true',
        help = 'Quiet mode, no logging of output')
    args = parser.parse_args()
    
    if args.ndays < 0 or \
    args.killswitch <= 0 or \
    not coordinates_valid(args.coordinates) or (args.verbose and args.quiet):
        parser.print_help()
        exit()

    # configure logging level
    level = logging.DEBUG if args.verbose else logging.INFO
    level = logging.CRITICAL if args.quiet else level
    log.setLevel(level)

    KILL_SWITCH = args.killswitch

    # test out all the things most likely to explode before going dark if
    # this will run as a daemon
    DOWNLOAD_DIR = args.download

    try:
        os.makedirs(DOWNLOAD_DIR)
    except FileExistsError:
        pass
    except OSError as exp:
        raise exp

    # note that daemonization somehow breaks the link between the process and UNIS,
    # so don't start up Runtime or Session instances here

    if args.daemon:
        with daemon.DaemonContext( 
        #stdout=sys.stdout,stderr=sys.stderr, # for debugging
        signal_map={signal.SIGTERM: shutdown,signal.SIGTSTP: shutdown},
        chroot_directory=None,
        working_directory=get_script_dir()):

            begin(args)
    else:
        begin(args)

def begin(args):
    # use fqdn to determine local endpoints
    name = socket.gethostname()
    fqdn = socket.getfqdn()

    LOCAL_DEPOT={"ibp://{}:6714".format(fqdn): { "enabled": True}}
    LOCAL_UNIS = "http://{}:{}".format(fqdn, LOCAL_UNIS_PORT)

    urls = [{"default": True, "url": LOCAL_UNIS}]
    opts = {"cache": { "preload": ["nodes", "services", "exnodes"]}}

    rt = Runtime(urls, **opts)
    sess = libdlt.Session(rt, bs="5m", depots=LOCAL_DEPOT, threads=1)

    # get the names of exnodes already present in UNIS
    exnodes_present = []
    for x in rt.exnodes:
        exnodes_present.append(x.name)

    # get the list of recent USGS Landsat images
    m_url2metadata, m_url2files_to_upload = download_recent_USGS_TIFFS(args.ndays,exnodes_present,args.coordinates) 

    # m_url2files_to_upload.keys is a subset of m_url2metadata.keys, possibly a strict subset
    for U in m_url2files_to_upload:
        metadata = m_url2metadata[U]
        files_to_upload = m_url2files_to_upload[U]
        fn_path = files_to_upload

        for F in files_to_upload:
            fn,fn_path = F
            time_to_insert,exn = sess.upload(filepath=fn_path)
            #time_to_insert,exn = sess.upload(filepath='./app.py')
            add_metadata(exn,metadata,fn)
            log.info('Inserted exnode %s' % fn)

if __name__ == "__main__":
    main()
