import os

from dotenv import main

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from utils.directory import create_directory
from utils.scraper import fonts, html, manifest, scripts

main.load_dotenv()
    
def main():

    # start web driver
    driver = webdriver.Chrome(service=Service(os.getenv('CHROME_DRIVER_PATH')))
    
    # generate scraped directory
    create_directory(os.getenv('PARENT_FOLDER'))
    
    # scrape fonts
    fonts(driver)
    
    #scrape html
    html(driver)
    
    #scrape manifest
    manifest(driver)
    
    #scraper scripts
    scripts(driver)
    
    assert "No results found." not in driver.page_source

    # close web driver
    driver.close()

if __name__ == "__main__":
    main()