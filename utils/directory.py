import os

def create_directory(path):
    try:
        os.mkdir(path, 0o66)
    except OSError as error:
        print(error)
        
def create_directories(path):
    try:
        os.makedirs(path, 0o66)
    except OSError as error:
        print(error)