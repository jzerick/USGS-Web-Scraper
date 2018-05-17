
from search import *
from cloudstoragedriver import Cloud

import daemon
import os
import time
import argparse
import socket
import threading
import lace, logging
import subprocess

import libdlt
from unis.runtime import Runtime

UNIS_URL="http://localhost:8888"
LOCAL_UNIS_HOST="localhost"
LOCAL_UNIS_PORT=9000
DOWNLOAD_DIR = "/home/wdln/scraper/data"

# stop downloading after this many scenes (buckets)
KILL_SWITCH = 9 # remove later or set to -1 to disable

log = lace.logging.getLogger("landsat_retriever")
log.setLevel(logging.INFO)

# to run a simple test replace <YOUR EMIAL> and <YOUR PASSWORD> with a dummy
# gmail account or your own.
'''
    TODO: create encrypted config file with dummy email creds.
    TODO: daemonize the app, make it a command line tool.
    TODO: convert TIFFs to exnodes and push them to UNIS.
    TODO: hand off TIFFs to DLT
    TODO: On sys exit clean up processes
    TODO: logging? D:
    TODO: Tests.
'''

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
    q = Query()
    m_url2metadata = q.find_n_days_old(n,coordinates)

    print("\nFiles to be downloaded: ", len(m_url2metadata), '\n')

    # Instantiate the web scraper to find urls in each bucket.
    # This is a dummy email I don't care about uploading to git, too lazy to make an encrypted config file atm.
    # dont use above, just filler for if the web scraper ever becomes a thing again

    C = Cloud(path = '/data')
    m_url2files_to_upload = {}

    scene_count = 0
    # for each bucket, get the relevant urls and download them.
    for url in m_url2metadata:
        scene_count += 1
        print('\n Working on %s of %s Buckets.' % (scene_count, len(m_url2metadata)))
        print('\n Fetching Bucket: ', url)

        m_url2files_to_upload[url] = C.DownloadBucket(url,exnodes_present)

        if KILL_SWITCH > 0 and scene_count > KILL_SWITCH:
            print('KILL SWITCH ENGAGED')
            break

    print(scene_count, " scenes added.")

    return m_url2metadata,m_url2files_to_upload

# from the WildfireDLN dln_ferry,
# https://github.com/datalogistics/wildfire-dln/blob/master/ferry/dln_ferry.py
def init_runtime(remote, local, local_only):
    while True:
        try:
            if local_only:
                urls = [{"default": True, "url": local}]
                opts = {"cache": { "preload": ["nodes", "services", "exnodes"]}}
                log.debug("Connecting to UNIS instance(s): {}".format(local))
            else:
                urls = [{"default": True, "url": remote}, {"url": local}]
                opts = {"cache": { "preload": ["nodes", "services"] }, "proxy": { "defer_update": False }}
                log.debug("Connecting to UNIS instance(s): {}".format(remote+','+local))
            rt = Runtime(urls, **opts)
            return rt
        except Exception as e:
            #import traceback
            #traceback.print_exc()
            log.warn("Could not contact UNIS servers {}, retrying...".format(urls))
        time.sleep(5)

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

    # get the approximate center for ease of visualization
    exn.properties.center_lat = (exn.properties.north_lat + exn.properties.south_lat)/2.
    exn.properties.center_long = (exn.properties.west_lon + exn.properties.east_lon)/2.

    exn.properties.rt_code = RT_code
    exn.properties.DELETE_ME = 'True %d' % KILL_SWITCH

def main():
    global DOWNLOAD_DIR

    # borrowed from the EODN Harvester, 
    # https://github.com/datalogistics/eodn-harvester/blob/master/eodnharvester/app.py
    # and the WildfireDLN dln_ferry,
    # https://github.com/datalogistics/wildfire-dln/blob/master/ferry/dln_ferry.py
    parser = argparse.ArgumentParser(description = "Harvest Landsat 8 data for WildfireDLN")
    parser.add_argument('-w', '--download', type=str, default=DOWNLOAD_DIR,
        help='Set local download directory')
        
    parser.add_argument('-n', '--ndays', type=int, default=7,
        help = "Retrieve only images captured in the last n days (default is n=7)")
        
    parser.add_argument('-c', '--coordinates', type=str, default=None,
        help = "Retrieve only images containing the specified coordinates as latitude,longitude, e.g. -c-8.0,137.0")
        
    parser.add_argument('-d', '--daemon', action = 'store_true', 
        help = "Indicates that the process should be run as a daemon")
        
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Produce verbose output from the script')
        
    parser.add_argument('-q', '--quiet', action='store_true',
        help='Quiet mode, no logging of output')
    args = parser.parse_args()

    if args.ndays < 0 or not coordinates_valid(args.coordinates) or (args.verbose and args.quiet):
        parser.print_help()
        exit()

    # configure logging level
    level = logging.DEBUG if args.verbose else logging.INFO
    level = logging.CRITICAL if args.quiet else level
    log.setLevel(level)

    name = socket.gethostname()
    fqdn = socket.getfqdn()

    DOWNLOAD_DIR = args.download
    try:
        os.makedirs(DOWNLOAD_DIR)
    except FileExistsError:
        pass
    except OSError as exp:
        raise exp

    # use fqdn to determine local endpoints
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
            add_metadata(exn,metadata,fn)
            print('inserted exnode',fn)

if __name__ == "__main__":
    main()
