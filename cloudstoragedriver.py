from google.cloud import storage
from google.cloud.storage import Blob
import sys
import os

class Cloud():
    def __init__(self, log,path='data/'):
        self.path = path

        # rather than link (and distribute) a service account, we rely on the
        # user to supply credentials by setting the environment variable
        # GOOGLE_APPLICATION_CREDENTIALS to the path of the service account file.
        self.client = storage.Client() 
        self.landsat_bucket = 'gcp-public-data-landsat'
        self.log = log

    """
        Downloads a single Bucket of Tiffs from the paste week's worth of USGS Satellite data using Google Cloud API.
    """
    def DownloadBucket(self, bucketID,exnodes_present):

        blob_uri =  bucketID.split(self.landsat_bucket)[1] + '/'
        self.log.info('Fetching blob %s' % blob_uri)
        bucket = self.client.get_bucket(self.landsat_bucket)
        blobs = bucket.list_blobs(prefix=blob_uri[1:])

        directory = self.path + blob_uri
        blob_names = []

        for b in blobs:
            # already have this one? skip.
            if b.name in exnodes_present:
                continue

            self.log.info('+ %s ' % b.name)
            blob_file_name = b.name.split('/')[-1]
            datapath = self.ensure_path(self.path, blob_uri, blob_file_name)
            with open(datapath + blob_file_name, 'wb') as file_obj:
                b.download_to_file(file_obj)
            blob_names.append([b.name, datapath + blob_file_name])

        return blob_names

    # thanks Stack Overflow :D
    def ensure_path(self, datapath, blob_uri, blob_name):

        cd = os.getcwd()
        path = cd + datapath + blob_uri

        if not os.path.exists(path):
            os.makedirs(path)
            open(path + blob_name, 'w').close()

        return path
