# Harvester Lite

Scrapes Google Storage website and API for USGS satellite TIFFS. From these TIFF files
we take the relevant metadata, push them out to UNIS, and then send the files to DLT
to be stored.

## TODO

- Run as a Daemon? Make the app 'listen' for new files? Or just add command line options for periodic polling? Currently polls everything within the last week.
- add logging

## IMPORTANT

After install, just run `app.py`. _No longer using Selenium to scrape HTML, instead using Google's poorly documented Python libraries._
Leaving in Web Scrapping stuff in case someone wants to try it or I ever decide to use Selenium for this again.

## Getting Started 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

* Python 3.4 or >


### Installing

Run `python3 setup.py build install` (perhaps in a local python virtual env).
Use `python3 app.py` to begin fetching USGS landsat data.



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
