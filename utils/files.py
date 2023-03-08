def write(file_path, method, text):
    f = open(file_path, method)
    f.write(text)
    f.close()