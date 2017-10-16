import wget
import os

class TiffBucket():
    '''
        TiffBucket class is created during the scraping performed by Scrape class.
        URLs to Tiff files are stored and massaged in the Bucket class. Google storage
        website does not pass the correct links in their HREFS, to the tail of the links
        need to be changed to reflect a header we can download from.
    '''
    def __init__(self, SENSOR_ID, PATH, ROW, SCENE_ID):

        self.TIFF_HREFS = []
        self.TXT_METADATA = ''
        self.SENSOR_ID = SENSOR_ID
        self.PATH = PATH
        self.ROW = ROW
        self.SCENE_ID = SCENE_ID
        self.NEW_URL = "http://storage.googleapis.com/gcp-public-data-landsat/"
        self.OLD_URL = "https://storage.cloud.google.com/gcp-public-data-landsat/"


    def add(self, href):
        '''
            Hrefs getting appended to a list in the Bucket. If the href is a TXT file,
            we remember that separately since we need information in that to create exnodes.
            Each href gets the front part of it changed to a header we can download from.
        '''
        if href[-4:] == ".txt":
            self.TXT_METADATA = href.replace(self.OLD_URL, self.NEW_URL)
        else:
            href = href.replace(self.OLD_URL, self.NEW_URL)
            print("adding... " + href)
            self.TIFF_HREFS.append(href)

    def download_file(self, url):

        local_filename = url.split('/')[-1]
        datapath = "data/" + self.SENSOR_ID + "/PRE/" + self.PATH + "/" + self.ROW + "/" + self.SCENE_ID + "/"

        # Check if there is a directory available for this Sat Path
        try:
            if not os.path.exists(datapath):
                os.makedirs(datapath)
        except Exception:
            print("Could not create the Directory for Downloaded Files..")

        # wget is used so I could easily show the download bar.
        # if needed requests could be used here instead.
        tiff = wget.download(url, out=datapath)
        print("\nFILE " + local_filename +" ADDED TO: "+ datapath)
        return local_filename

    def download_bucket(self):
        for href in self.TIFF_HREFS:
            print("\nDOWNLOADING - " + href.split('/')[-1])
            self.download_file(href)

        self.download_file(self.TXT_METADATA)

        print("\nBUCKET DOWNLOADED SUCCESSFULLY")

        return
