import os

from dotenv import main

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from utils.directory import create_directory
from utils.scraper import html, scripts, files

main.load_dotenv()
    
def main():
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    
    # start web driver
    driver = webdriver.Chrome(service=Service(os.getenv('CHROME_DRIVER_PATH')), desired_capabilities=capabilities)
    
    # generate scraped directory
    create_directory(os.getenv('PARENT_FOLDER'))
    
    #scrape html
    html(driver)
    
    #scrape scripts
    scripts(driver)
    
    # scrape fonts
    files()
    
    assert "No results found." not in driver.page_source

    # close web driver
    driver.close()

if __name__ == "__main__":
    main()