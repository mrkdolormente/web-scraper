def write(file_path, method, content, encoding=None):
    with open(file_path, method, encoding=encoding) as f:
        f.write(content)
        f.close()