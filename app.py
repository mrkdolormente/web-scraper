import os
import time
from dotenv import main

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from utils.directory import create_directory, create_directories
from utils.files import write

main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')
parent_folder = os.getenv('PARENT_FOLDER')

# start web driver
driver = webdriver.Chrome(os.getenv('CHROME_DRIVER_PATH'))
driver.get(website_link)
assert "Class Central" in driver.title

# generate scraped directory
create_directory(parent_folder)

html = driver.page_source
index_file = parent_folder + '/index.html'

# create index file
write(index_file, 'w', '<!DOCTYPE html>')
write(index_file, 'a',html.encode('utf-8') )

# scrape links
links = driver.find_elements(By.TAG_NAME, 'a')

link_details = [];

for link in links:
    href = link.get_attribute('href')
    path = href.replace(website_link, '')
    
    if website_link in href and path:
        link_details.append({
            'href': href.encode('utf-8'),
            'path': path.encode('utf-8')
        })
        
for detail in link_details:
    href = detail['href']
    path = detail['path']
    
    print(href, path)
    
    driver.get(href)
        
    relative_path = parent_folder + '/' + path.encode('utf-8');
    inner_index_file = relative_path + '/' + 'index.html'
    inner_html = driver.page_source
    
    create_directories(relative_path) 
    
    # create index file
    write(inner_index_file, 'w', '<!DOCTYPE html>')
    write(inner_index_file, 'a', inner_html.encode('utf-8') )
        
print(link_details)

assert "No results found." not in driver.page_source

# close web driver
driver.close()