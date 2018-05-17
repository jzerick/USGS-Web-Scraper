from google.cloud import storage
from google.cloud.storage import Blob
import sys
import os

class Cloud():
    def __init__(self, path='data/'):
        self.path = path
        self.client = storage.Client.from_service_account_json('config/service_account.json')
        self.landsat_bucket = 'gcp-public-data-landsat'


    """
        Downloads a single Bucket of Tiffs from the paste week's worth of USGS Satellite data using Google Cloud API.
    """
    def DownloadBucket(self, bucketID,exnodes_present):

        blob_uri =  bucketID.split(self.landsat_bucket)[1] + '/'
        print("FETCHING BLOB - ", blob_uri)
        bucket = self.client.get_bucket(self.landsat_bucket)
        blobs = bucket.list_blobs(prefix=blob_uri[1:])

        directory = self.path + blob_uri
        blob_names = []

        for b in blobs:
            # already have this one? skip.
            if b.name in exnodes_present:
                continue

            print('BLOB NAME: ', b.name)
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
