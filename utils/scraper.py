import os
import json
import re

from dotenv import main

from selenium.webdriver.common.by import By

from utils.directory import create_directories
from utils.files import write, download, open_list
from utils.helper import update_link_files, get_links
from utils.translate import page

main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')
parent_folder = os.getenv('PARENT_FOLDER')

def html(driver):
    print('START:: HTML')

    driver.get(website_link)
    assert "Class Central" in driver.title
    
    file_link_details = [
        {
            'path': 'files/scraper_js.json',
            'in_filter': ['.js']
        },
        {
            'path': 'files/scraper_files.json',
            'in_filter': ['.png', '.svg', '.webmanifest', '.woff2']
        },
    ]
    
    # update link files to be use for script and files downloading and scraping
    index_links = get_links(driver)
    update_link_files(index_links, file_link_details)

    driver.execute_script("window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: \"smooth\" })")

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
                link_counter = 0
                
                for link in links:
                    href = link.get_attribute('href')
                    path = href.replace(website_link, '')
                    
                    link_counter += 1
                    
                    is_exist = len([x for x in link_details_list if x['path'] == path]) != 0
                    
                    if website_link in href and path and not is_exist:
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
                
                # update link files to be use for script and files downloading and scraping
                inner_links = get_links(driver)
                update_link_files(inner_links, file_link_details)
                    
                relative_path = parent_folder + '/' + path;
                inner_index_file = relative_path + '/' + 'index.html'
                inner_html = driver.page_source
                
                create_directories(relative_path) 
                
                # translate page to hindi
                translated_html = page(inner_html, language, convert_links=True)
                
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
            font_folders.insert(0, parent_folder)
            
            font_counter += 1
            print('DOWNLOADING::', parent_folder + '/' + font, font_counter, len(downloaded_fonts))
            
            create_directories('/'.join(font_folders))
            print(website_link + font, parent_folder + '/' + font)
            
            response = download(website_link + font)
            
            write(parent_folder + '/' + font, 'wb', response.content)
            
    print('FINISHED:: FONTS')
    
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
        
        script_element = driver.find_element(By.TAG_NAME, 'pre')
        jsscript = script_element.get_attribute('innerText')
        write(parent_folder + '/' + script.replace(website_link, ''), 'w', jsscript, 'utf-8')

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