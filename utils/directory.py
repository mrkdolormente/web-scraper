import os

def create_directory(path):
    try:
        os.umask(0)
        os.mkdir(path, 0o777)
    except OSError as error:
        print(error)
        
def create_directories(path):
    try:
        os.umask(0)
        os.makedirs(path, 0o777)
    except OSError as error:
        print(error)