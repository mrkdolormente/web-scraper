import os
import re
import time

from dotenv import main

from selenium.webdriver.common.by import By

from utils.directory import create_directories
from utils.files import write, download, open_list
from utils.helper import update_link_files, get_links
from utils.translate import page

main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')
parent_folder = os.getenv('PARENT_FOLDER')

def html(driver, files_only=False, scripts_only=False):
    print('START:: HTML')

    driver.get(website_link)
    assert "Class Central" in driver.title
    
    file_link_details = []
    
    include_html = (not files_only and not scripts_only)
    
    if files_only or include_html:
        file_link_details.append({
            'path': 'files/scraper_files.json',
            'in_filter': ['.png', '.svg', '.webmanifest', '.woff2'],
            'not_in_filter': ['catalog-iframe']
        })
        
    if scripts_only or include_html:
        file_link_details.append({
            'path': 'files/scraper_js.json',
            'in_filter': ['.js'],
            'not_in_filter': ['catalog-iframe']
        })
    
    # update link files to be use for script and files downloading and scraping
    if len(file_link_details) != 0:
        index_links = get_links(driver)
        update_link_files(index_links, file_link_details)

    if include_html:
        html = driver.page_source
        index_file = parent_folder + '/index.html'
        
        language = os.getenv('TRANSLATE_LANG')
        
        # translate page to hindi
        translated_html = page(html, language, convert_links=True)

        # create index file
        write(index_file, 'w', '<!DOCTYPE html>')
        write(index_file, 'a', translated_html, 'utf-8')

    # scrape links
    links = driver.find_elements(By.TAG_NAME, 'a')
    link_details_list = []

    retry = 0
    trigger = True
    
    while trigger:
        try:
            for link in links:
                href = link.get_attribute('href')
                path = href.replace(website_link, '')
                
                is_exist = len([x for x in link_details_list if x['path'] == path]) != 0
                
                if website_link in href and path and not is_exist:
                    link_details_list.append({
                        'href': href,
                        'path': path
                    })
                    
            link_details = []
            
            if len(file_link_details) != 0 and not include_html:
                link_details = link_details_list
            else:
                link_details = [x for x in link_details_list if not os.path.exists(parent_folder + '/' + x['path'])]
                
                        
            counter = 0
                        
            for detail in link_details:
                href = detail['href']
                path = detail['path']
                
                counter += 1;
                print('SCRAPING::', href, path, counter, len(link_details))
                
                driver.get(href)
                time.sleep(3)
                
                # update link files to be use for script and files downloading and scraping
                if len(file_link_details) != 0:
                    inner_links = get_links(driver)
                    update_link_files(inner_links, file_link_details)
                    
                if include_html:
                    relative_path = parent_folder + '/' + path;
                    inner_index_file = relative_path + '/' + 'index.html'
                    inner_html = driver.page_source
                    
                    # translate page to hindi
                    translated_html = page(inner_html, language, convert_links=True)
                    
                    create_directories(relative_path) 
                    
                    # create index file
                    write(inner_index_file, 'w', '<!DOCTYPE html>')
                    write(inner_index_file, 'a', translated_html, "utf-8" ) 
                
            trigger = False
        except Exception as error:
            retry += 1
            trigger = retry <= 3
            
            print('RETRY::', retry)
            
            if not trigger:
                print('RETRY::ERROR', error)    
        
    print('FINISHED:: HTML')
    
def files():
    print('START:: FILES')

    files_link = open_list('files/scraper_files.json')

    files_counter = 0

    for link in files_link:
        folders = link.replace(website_link, '').split('/')
        folders.pop()
        folders.insert(0, parent_folder)
        
        files_counter += 1
        
        create_directories('/'.join(folders))
        
        print('DOWNLOAD::', files_counter, len(files_link))
        response = download(link)
        
        write(parent_folder + '/' + link.replace(website_link, ''), 'wb', response.content)
            
    print('FINISHED:: FILES')
    
def scripts(driver):
    print('START:: SCRIPTS')
    
    script_links = open_list('files/scraper_js.json')
            
    script_counter = 0
            
    for script in script_links:
        href = script
        
        folders = script.replace(website_link, '').split('/')
        folders.pop()
        folders.insert(0, parent_folder)
        
        create_directories('/'.join(folders))
        
        script_counter += 1
        print('SCRAPING::', href, script_counter, len(script_links))
        
        driver.get(href)
        time.sleep(3)
        
        script_element = driver.find_element(By.TAG_NAME, 'pre')
        jsscript = script_element.get_attribute('innerText')
        
        write(parent_folder + '/' + script.split('?')[0].replace(website_link, ''), 'w', jsscript, 'utf-8')

    print('FINISHED:: SCRIPTS')
    
def link_rel(driver):
    print('START:: LINK_REL')
    
    driver.get(website_link)
    assert "Class Central" in driver.title
    
    rel_list = ['manifest', 'apple-touch-icon', 'icon', 'mask-icon', 'search']
    
    for rel in rel_list:
        script_element = driver.find_element(By.CSS_SELECTOR, 'link[rel="'+ rel +'"]')
        
        if script_element:
            href = script_element.get_attribute('href')
            
            print('DOWNLOADING::', rel, href)
            
            response = download(href)
            
            write(parent_folder + '/' + href.replace(website_link, ''), 'wb', response.content)
    
    print('FINISHED:: LINK_REL')