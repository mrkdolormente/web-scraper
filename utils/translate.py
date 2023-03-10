from googletrans import Translator
from bs4 import BeautifulSoup


def translate(text, dest):
    translator = Translator()
    translate = translator.translate(text, dest=dest)
    return translate.text

def page(html, dest):
    soup = BeautifulSoup(html, features="html.parser")
    text_elements = [element for element in soup.find_all(string=True) if element.parent.name not in ['script', 'style']]

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