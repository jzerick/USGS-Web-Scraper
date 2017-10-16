from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os

from bucket import TiffBucket

# TODO: Write a setup.py file for easy intall.
# TODO: Write some docs on dependecies.

class Scraper():
    '''
        Web Scraper Class for fetching LandSat images from google.
        Because most of the HTML we need to fetch to download a TIFF is
        rendered through Javascript in the Cloud Storage Web App, we rely on Selenium
        to get access to the parts of the page we need.
    '''

    def __init__(self, gmail=None, password=None, headless=True, driver="geckodriver"):
        '''
            :gmail: Initialize gmail account. Email is needed to authenticate to get html.
            :password: Initialize password for email.
            :headless: default - initialize to PhantomJS for headless scraping.
            :driver: String to set Selenium Web Driver, supports ghostdriver, geckodriver, chromedriver.
        '''
        # Driver will default to Chrome, if false driver is set to Firefox
        if headless == True:
            print("Starting Headless Browser... \n")
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1200x600')
            path = str(os.path.dirname(os.path.realpath(__file__)) + "/webdriver/chromedriver")
            print(path)
            path = str(os.system("which chromedriver"))

            self.driver = webdriver.Chrome(chrome_options=options)

        else:
            self.setDriver(driver)

        print("Using: " + self.driver.name)

        self.EMAIL = gmail
        self.PASSWORD = password
        self.LAND_SAT_URL = "https://console.cloud.google.com/storage/browser/gcp-public-data-landsat/"
        self.BUCKET_URL = "https://console.cloud.google.com/storage/browser/gcp-public-data-landsat/"

    def authenticate(self, user=None, passphrase=None):
        '''
        Selenium script to log into google on start up. You must be logged into a gmail account
        to view the USGS storage pages.

        :params:
        :user: A string of a valid gmail account.
        :password: A string of associated password with the gmail account.

        '''
        if user == None or passphrase == None:
            user = self.EMAIL
            passphrase = self.PASSWORD

        self.driver.get(self.BUCKET_URL)

        print("\nAttempting to authenticate " + self.EMAIL + " to Google Storage Site.\n")

        # selenium commands for inputting and submitting login creds
        username = self.driver.find_element_by_id("identifierId")
        username.send_keys(user)
        username.send_keys(Keys.RETURN)
        print("Entered Email.")


        self.driver.implicitly_wait(3)
        password = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.NAME, "password")))
        print("Entered Pass\n")

        passwordNext = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "passwordNext")))
        password.send_keys(passphrase)
        passwordNext.click()
        #password.send_keys(Keys.RETURN)

        return

    def get_status_code(self):
        url = self.driver.current_url
        print("Checking Status of ", url, "...")
        r = requests.get("url")
        code = r.status_code
        print(code)
        return


    def setDriver(self, driver_name):
        # Turns out phantomJS isnt so great with Python Selenium.
        try:
            if driver_name == "ghostdriver":
                self.driver = webdriver.PhantomJS()
            elif driver_name == "chromedriver":
                self.driver = webdriver.Chrome()
            elif driver_name == "geckodriver":
                self.driver = webdriver.Firefox()
            else:
                print("Driver Name not recognized.")
        except Exception:
            print("Failed to connect to Driver...")
            print("Please ensure the requested driver is in your PATH...")

        return

    def buildUrl(self, SENSOR_ID, PATH, ROW, SCENE_ID):
        '''
            /[SENSOR_ID]/PRE/[PATH]/[ROW]/[SCENE_ID]/

            The components of this path are:

            [SENSOR_ID]: An identifier for the particular satellite and camera sensor.
            [PATH]: The WRS path number.
            [ROW]: The WRS row number.
            [SCENE_ID]: The unique scene ID.

            ex) gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/

        '''
        url = self.LAND_SAT_URL + SENSOR_ID + "/PRE/" + PATH + "/" + ROW + "/" + SCENE_ID

        return url


    def ScrapeBucket(self, SENSOR_ID, PATH, ROW, SCENE_ID):
        '''
            /[SENSOR_ID]/PRE/[PATH]/[ROW]/[SCENE_ID]/

            The components of this path are:

            [SENSOR_ID]: An identifier for the particular satellite and camera sensor.
            [PATH]: The WRS path number.
            [ROW]: The WRS row number.
            [SCENE_ID]: The unique scene ID.

            ex) gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/

            Output: A Bucket Objects that contains all the information needed
            to download the file and convert metadata to exnode.

        '''
        # Build the URL of the bucket we want to get.
        self.BUCKET_URL = self.buildUrl(SENSOR_ID, PATH, ROW, SCENE_ID)
        print("\nAttempting to fetch bucket at... ", self.BUCKET_URL)

        # Have Selenium auto authenticate and proceed to the URL containing the bucket.
        self.authenticate()

        if (self.driver.title == "Error 400 (Not Found)!!1"):
            print("page not found")

        # Detect the table, wait for it to load
        tiff_table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'p6n-storage-objects-table')))

        # Convert Table Element to HTML and parse it with BS4.
        soup = BeautifulSoup(tiff_table.get_attribute('innerHTML'), 'html.parser')
        rows = soup.findAll("span", { "class" : "p6ntest-cloudstorage-object-link" })

        TB = TiffBucket(SENSOR_ID, PATH, ROW, SCENE_ID)

        for span in rows:
            TB.add(span.a['href'])

        return TB
