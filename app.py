import os
import re
import wget

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

print('START:: HTML')

driver.get(website_link)
assert "Class Central" in driver.title

driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

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
        
counter = 0;
        
for detail in link_details:
    href = detail['href']
    path = detail['path']
    
    
    counter += 1;
    print('SCRAPING::', href, path, counter, len(link_details))
    
    driver.get(href)
        
    relative_path = parent_folder + '/' + path.encode('utf-8');
    inner_index_file = relative_path + '/' + 'index.html'
    inner_html = driver.page_source
    
    create_directories(relative_path) 
    
    # create index file
    write(inner_index_file, 'w', '<!DOCTYPE html>')
    write(inner_index_file, 'a', inner_html.encode('utf-8') )
    
print('FINISHED:: HTML')

print('START:: FILES')

driver.get(website_link)
assert "Class Central" in driver.title

file_links = [];

script_links = [];
script_elements = driver.find_elements(By.TAG_NAME, 'script')

for element in script_elements:
    script = element.get_attribute('src')
    print(script)
    if website_link in script:
        script_links.append(script.replace(website_link, ''))
        
file_links.extend(script_links)

html = driver.page_source
font_links = re.findall("url\(/(.*?)\) format\(\"woff2\"\)", html)

file_links.extend(font_links)

file_counter = 0
downloaded_files = []

for link in file_links:
    file = link.encode('utf-8')
    
    if file not in downloaded_files:
        file_folders = file.split('/')
        file_folders.pop();
        
        create_directories(parent_folder + '/' + '/'.join(file_folders))
        
        wget.download(website_link + file, parent_folder + '/' + file)
        
        downloaded_files.append(file)
        
        file_counter += 1
        print('DOWNLOADED::', parent_folder + '/' + file, file_counter, len(file_links))
        
print('FINISHED:: FILES')

assert "No results found." not in driver.page_source

# close web driver
driver.close()