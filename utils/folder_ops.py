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

def within_subdir(path, start, proper=False):
    rel_path = os.path.relpath(path, start)
    if rel_path.startswith('..'):
        return False
    elif rel_path == '.':
        # proper=True, same path is not proper subdir
        # proper=False, same path is subdir
        return not proper
    else:
        return True

def is_samepath(path1, path2):
    path1_norm = os.path.normpath(path1)
    path2_norm = os.path.normpath(path2)
    return path1_norm == path2_norm

def get_rel_depth(path, start):
    if within_subdir(path, start, proper=True):
        rel_path = os.path.relpath(path, start)
        depth = rel_path.count(os.path.sep) + 1
        return depth
    elif is_samepath(path, start):
        return 0
    else:
        return -1 

def get_folderlist_by_depth(path, depth):
    path = os.path.normpath(path)
    res = []
    for root, dirs, files in os.walk(path, topdown=True):
        cur_depth = get_rel_depth(root, path) + 1
        if cur_depth == depth:
            res += [os.path.join(root, d) for d in dirs]
            res += [os.path.join(root, f) for f in files]
            dirs[:] = [] # Don't recurse any deeper
    
    return res
