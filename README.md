# Harvester Lite

The USGS Landsat Google Cloud Public Dataset is a Bigtable containing metadata that when queried, provides users references (URLs) to retrieve the satellite imagery and associated files. Rather than attempting to navigate through encoded directory names, we can use this metadata to index and obtain imagery of interest.

To access this dataset, the user must have the proper credentials, specifically, a service account. See here for instructions on obtaining one: https://cloud.google.com/docs/authentication/getting-started

Usually the service account credentials are stored in JSON format in a local file. For authentication to work, the user must set an environmental variable containing the path to the file, e.g.:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/file.json"

Once authenticated, the script downloads data en masse and uploads it via libdlt. 

# Running the harvester

usage: temp.py [-h] [-w DOWNLOAD] [-n NDAYS] [-k KILLSWITCH] [-c COORDINATES]
               [-d] [-v] [-q]

Harvest Landsat 7/8 data for WildfireDLN

optional arguments:
  -h, --help            show this help message and exit
  -w DOWNLOAD, --download DOWNLOAD
                        Set local download directory
  -n NDAYS, --ndays NDAYS
                        Retrieve only images captured in the last n days
                        (default is n=7)
  -k KILLSWITCH, --killswitch KILLSWITCH
                        Enable and activate kill switch after retrieving k
                        buckets (default is disabled)
  -c COORDINATES, --coordinates COORDINATES
                        Retrieve only images containing the specified
                        coordinates as latitude,longitude, e.g. -c-8.0,137.0
  -d, --daemon          Indicates that the process should be run as a daemon
  -v, --verbose         Produce verbose output from the script
  -q, --quiet           Quiet mode, no logging of output

# Some details and examples

The usual verbose, quiet, and help options act as expected. By default the script checks the Cloud for files created within the last seven days, but this can be changed with the -n option. The user can indicate interest in a particular location, specified as latitude/longitude coordinates with the -c option. For testing purposes a killswitch is available; the -k option enables a killswitch to be activated after so many "Buckets" (Landsat scenes) are downloaded.

If the user wishes to search files created in the last 10 days, at location latitude=-8 and longitude=137, but stop after downloading 3 scenes matching those characteristics, the following will suffice:

python3 app.py -n10 -c-8,137 -k3

A download directory can additionally be specified with the -w option, e.g.:

python3 app.py -n10 -c-8,137 -k3 -w/path/to/data/store

And if the user wishes for all of this to occur in the background, -d will daemonize the process.

### Everything below is deprecated but still functional, leaving in my personal repo (should be ripped out before heading to data-logistics repo)

You need to have chromedriver inside of your path to run headless. To run a full featured
browser you need to have geckodriver installed in your path.

On Mac just use `brew install geckodriver` and brew `install chromedriver`.

No workflow found for windows. If you need to use windows you'll have to google how
to get geckodriver and chromedriver in the right place to run Selenium.

For CentOS deployment run the script ` webdriver/centos_chromedriver.sh `. CentOS deployment only needs the chromedriver since there is generally no GUI
to run the full browser from a terminal.

CentOS also needs protobuf library, but for whatever reason it doesnt install correctly on CentOS using pip.
See here: https://blog.jeffli.me/blog/2016/12/08/install-protocol-buffer-from-source-in-centos-7/ to install it.
It takes forever. If you have protobuf installed from your google-cloud python installation, you can run the app to
check if it works. If protobuf module can't be found and protobuf shows up in your python environment then you will
need to install the binaries unfortunately D: .

## Deployment

TODO: Build out a Daemon that automatically gets and pushes TIFFS. Build out something that can 'listen' to file changes?

## Built With

* [BS4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Granular Html Scraping
* [Selenium Web Driver](http://selenium-python.readthedocs.io/getting-started.html) - Selenium Python Web Driver for scraping Javascript driven sites.
* [DLT](https://github.com/datalogistics/dlt-web/blob/develop/public/js/map/TopologyMapController.js#L81) - DLT Upload code ripped from.
