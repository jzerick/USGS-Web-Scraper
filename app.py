from scraper import Scraper
from bucket import TiffBucket

# to run a simple test replace <YOUR EMIAL> and <YOUR PASSWORD> with a dummy
# gmail account or your own.
'''
    TODO: create encrypted config file with dummy email creds.
    TODO: daemonize the app, make it a command line tool.
    TODO: make it 'listen' and redownload buckets.
    TODO: convert TIFFs to exnodes and push them to UNIS.
    TODO: hand off TIFFs to DLT
'''

scraper = Scraper(gmail="<YOUR EMAIL>",password="<PASSWORD>",headless=True)

bucket = scraper.ScrapeBucket("LC08","044","034","LC80440342016259LGN00")
bucket.download_bucket()
