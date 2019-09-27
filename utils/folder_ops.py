import os

def get_size(path):
    if os.path.isdir(path):
        # the start_path is a regular folder
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    elif os.path.isfile(path):
        return os.path.getsize(path)

def get_folderlist_by_depth(path, depth):
    path = os.path.normpath(path)
    res = []
    for root, dirs, files in os.walk(path, topdown=True):
        cur_depth = root[len(os.path.sep):].count(os.path.sep) + 1
        if cur_depth == depth:
            res += [os.path.join(root, d) for d in dirs]
            res += [os.path.join(root, f) for f in files]
            dirs[:] = [] # Don't recurse any deeper
    
    return res
