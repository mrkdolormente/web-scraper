import json
import os
import requests

def write(file_path, method, content, encoding=None):
    print('WRITE::', file_path)
    
    with open(file_path, method, encoding=encoding) as f:
        f.write(content)
        f.close()
        
def download(url):
    print('DOWNLOAD::', url)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    return requests.get(url, headers=headers)

def open_list(file_path):
    list = []
    
    if os.path.isfile(file_path):
        f = open(file_path)
    
        list.extend(json.load(f))
        
    return list