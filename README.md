# Harvester Lite

Scrapes Google Storage website and API for USGS satellite TIFFS. From these TIFF files
we take the relevant metadata, push them out to UNIS, and then send the files to DLT
to be stored.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

* Python 3.4 or >
* chromedriver and geckodriver in your path. Check Installing section for getting set up.
I supplied the files for chromedriver and geckodriver in case you want to manually put them in your path.

### Installing

Run setup.py

You need to have chromedriver inside of your path to run headless. To run a full featured
browser you need to have geckodriver installed in your path.

On Mac just use `brew install geckodriver` and brew `install chromedriver`.

No workflow found for windows. If you need to use windows you'll have to google how
to get geckodriver and chromedriver in the right place to run Selenium.

For CentOS deployment run the script ` webdriver/centos_chromedriver.sh `. CentOS deployment only needs the chromedriver since there is generally no GUI
to run the full browser from a terminal.

## Deployment

TODO: Build out a Daemon that automatically gets and pushes TIFFS. Build out something that can 'listen' to file changes?

## Built With

* [BS4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Granular Html Scraping
* [Selenium Web Driver](http://selenium-python.readthedocs.io/getting-started.html) - Selenium Python Web Driver for scraping Javascript driven sites.
* [DLT](https://github.com/datalogistics/dlt-web/blob/develop/public/js/map/TopologyMapController.js#L81) - DLT Upload code ripped from.
