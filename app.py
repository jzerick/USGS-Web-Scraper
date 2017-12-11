from scraper import Scraper
from bucket import TiffBucket
from search import Query
from cloudstoragedriver import Cloud

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


def download_recent_USGS_TIFFS():
    '''
        Queries google for the last week of TIFFS uploaded from USGS.

        Downloads them to your file system based on the path laid out by Google.

    '''
    # fetch locations of TIFFS uploaded in the last week
    q = Query()
    urls = q.find_week_old()

    print("\nFiles to be downloaded: ", len(urls), '\n')

    # Instantiate the web scraper to find urls in each bucket.
    # This is a dummy email I don't care about uploading to git, too lazy to make an encrypted config file atm.
    #S = Scraper(gmail="crest14059@gmail.com", password="cr3st14059", headless=True)
    C = Cloud(path = '/data')
    filecount = 0
    # for each bucket, get the relevant urls and download them.
    for url in urls:
        filecount += 1
        print('\n Working on %s of %s Buckets.' % (filecount, len(urls) + 1))
        print('\n Fetching Bucket: ', url)
        bucket = C.GetBucket(url)
        print(bucket)

        #
        #bucket = S.Scrape_From_Bucket_URL(url)
        #bucket.download_bucket()


    print(filecount, " files added.")


download_recent_USGS_TIFFS()
