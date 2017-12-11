import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "USGS Google Storage Scraper",
    version = "0.0.1",
    author = "Grant Skipper",
    author_email = "gskipper@iu.edu",
    description = ("Provides a tool for scraping and downloading buckets of USGS TIFFS from Google Storage."),
    license = "BSD",
    long_description=read('README.md'),
    include_package_data = True,
      install_requires=[
          "wget",
          #"bs4",
          #"selenium",
          "google-cloud==0.27.0",
          "google-cloud-bigquery==0.27.0",
          "google-cloud-storage==1.6.0",
          "uuid"
      ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
