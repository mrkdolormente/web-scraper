import json
import os

from dotenv import main

from utils.directory import create_directories
from utils.files import write

main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')
parent_folder = os.getenv('PARENT_FOLDER')

def update_link_files(list, file_details=[]):
    create_directories('files')
    
    for item in file_details:
        in_filter = item['in_filter']
        filepath = item['path']
        
        links = [x['url'] for x in list if in_list(x['url'], in_filter)]
        print(links)
        
        file_details_list = []
        
        if os.path.isfile(filepath):
            f = open(filepath)
        
            file_details_list.extend(json.load(f))

        for link in links:
            if link not in file_details_list:
                file_details_list.append(link)
            
        write(filepath, 'w', json.dumps(file_details_list))

def get_links(driver):
    perf_logs = driver.get_log('performance')
    
    network_response_logs = [x for x in perf_logs if __is_onsite(x)]
    
    return list(map(__logs_attributes, network_response_logs))

def in_list(text, list=[]):
    print(text, list, '.manifest' in text)
    return len([x for x in list if x in text]) != 0
    
def __is_onsite(x):
    logs = __logs_attributes(x)
    url = logs['url']
    
    return website_link in url

def __logs_attributes(x):
    message_logs = json.loads(x['message'])
    method = message_logs['message']['method']
    
    url = ''
    if method == 'Network.responseReceived':
        url = message_logs['message']['params']['response']['url']
    elif method == 'Network.requestWillBeSent':
        url = message_logs['message']['params']['request']['url']
    
    return {
        'method': method,
        'url': url
    }
        