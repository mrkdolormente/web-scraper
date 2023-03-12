import os

from dotenv import main

from googletrans import Translator
from bs4 import BeautifulSoup

main.load_dotenv()

website_link = os.getenv('WEBSITE_LINK')

def translate(text, dest):
    translator = Translator()
    translate = translator.translate(text, dest=dest)
    return translate.text

def page(html, dest, convert_links=False):
    soup = BeautifulSoup(html, features="html.parser")
    text_elements = [element for element in soup.find_all(string=True) if element.parent.name not in ['script', 'style']]

    if convert_links:
        links = soup.find_all('a', href=True)
        
        for link in links:
            print('COVERT::OLD', link['href'])
            link['href'] = link['href'].replace(website_link, '/')
            print('COVERT::NEW', link['href'])
            
    element_counter = 0
    
    for element in text_elements:
        text = element.get_text(strip=True)
        
        element_counter += 1
        
        if not text:
            continue
        
        translated_text = translate(text, dest)
        element.replace_with(translated_text)
        
        print('TRANSLATE::', translated_text, element, element_counter, len(text_elements))
    
    return soup.prettify()