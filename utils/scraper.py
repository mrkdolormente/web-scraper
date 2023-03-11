import os
import json
import re

from dotenv import main

from selenium.webdriver.common.by import By

from utils.directory import create_directories
from utils.files import write, download
from utils.translate import page



main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')
parent_folder = os.getenv('PARENT_FOLDER')

def html(driver):
    print('START:: HTML')

    driver.get(website_link)
    assert "Class Central" in driver.title

    driver.execute_script("window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: \"smooth\" })")

    html = driver.page_source
    index_file = parent_folder + '/index.html'
    
    language = os.getenv('TRANSLATE_LANG')
    
    # translate page to hindi
    translated_html = page(html, language)

    # create index file
    write(index_file, 'w', '<!DOCTYPE html>')
    write(index_file, 'a', translated_html, 'utf-8')

    # scrape links
    links = driver.find_elements(By.TAG_NAME, 'a')
    link_details_list = []
    
    scraper_html_file = 'files/scraper_html.json'

    retry = 0
    trigger = True
    
    while trigger:
        try:
            print('ISFILE::', os.path.isfile(scraper_html_file))
            
            if os.path.isfile(scraper_html_file):
                f = open(scraper_html_file)
            
                link_details_list = json.load(f)
            else:
                create_directories('files')
                
                link_counter = 0
                
                for link in links:
                    href = link.get_attribute('href')
                    path = href.replace(website_link, '')
                    
                    link_counter += 1
                    
                    if website_link in href and path:
                        link_details_list.append({
                            'id': link_counter,
                            'href': href,
                            'path': path,
                            'is_scraped': False
                        })
                        
                write(scraper_html_file, 'w', json.dumps(link_details_list))
                
            link_details = [x for x in link_details_list if x['is_scraped'] == False]
                        
            counter = 0
                        
            for detail in link_details:
                href = detail['href']
                path = detail['path']
                key = detail['id']
                
                
                counter += 1;
                print('SCRAPING::', href, path, counter, len(link_details))
                
                driver.get(href)
                    
                relative_path = parent_folder + '/' + path;
                inner_index_file = relative_path + '/' + 'index.html'
                inner_html = driver.page_source
                
                create_directories(relative_path) 
                
                # translate page to hindi
                translated_html = page(inner_html, language)
                
                # create index file
                write(inner_index_file, 'w', '<!DOCTYPE html>')
                write(inner_index_file, 'a', translated_html, "utf-8" ) 
                
                link_details_list[key] = {
                    **detail,
                    'is_scraped': True
                }
                
                write(scraper_html_file, 'w', json.dumps(link_details_list))
                
            trigger = False
        except Exception as error:
            retry += 1
            trigger = retry <= 3
            
            print('RETRY::', retry)
            
            if not trigger:
                print('RETRY::ERROR', error)
            
        
    print('FINISHED:: HTML')

def fonts(driver):
    print('START:: FONTS')

    driver.get(website_link)
    assert "Class Central" in driver.title

    html = driver.page_source
    font_links = re.findall("url\(/(.*?)\) format\(\"woff2\"\)", html)

    font_counter = 0
    downloaded_fonts = []

    for link in font_links:
        font = link
        
        if font not in downloaded_fonts:
            font_folders = font.split('/')
            font_folders.pop();
            
            font_counter += 1
            print('DOWNLOADING::', parent_folder + '/' + font, font_counter, len(font_folders))
            
            create_directories(parent_folder + '/' + '/'.join(font_folders))
            print(website_link + font, parent_folder + '/' + font)
            
            response = download(website_link + font)
            
            write(parent_folder + '/' + font, 'wb', response.content)
            
    print('FINISHED:: FONTS')
    
def scripts(driver):
    print('START:: SCRIPTS')
    
    driver.get(website_link)
    assert "Class Central" in driver.title
    
    create_directories(parent_folder + '/' + 'webpack')
    
    script_links = [];
    script_elements = driver.find_elements(By.TAG_NAME, 'script')

    for element in script_elements:
        script = element.get_attribute('src')
        if website_link in script:
            script_links.append({
                'href': script,
                'path': script.replace(website_link, '')
            })
            
    script_counter = 0
            
    for script in script_links:
        href = script['href']
        path = script['path']
        
        script_counter += 1
        print('SCRAPING::', href, script_counter, len(script_links))
        
        driver.get(href)
        
        script_element = driver.find_element(By.TAG_NAME, 'pre')
        jsscript = script_element.get_attribute('innerText')
        write(parent_folder + '/' + path, 'w', jsscript, 'utf-8')

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