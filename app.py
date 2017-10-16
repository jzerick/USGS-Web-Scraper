from scraper import Scraper
from bucket import TiffBucket

# to run a simple test replace <YOUR EMIAL> and <YOUR PASSWORD> with a dummy
# gmail account or your own. TODO: create encrypted config file with dummy email creds.

scraper = Scraper(gmail="<YOUR EMAIL>",password="<YOUR PASSWORD>",headless=True)

bucket = scraper.ScrapeBucket("LC08","044","034","LC80440342016259LGN00")
bucket.download_bucket()
