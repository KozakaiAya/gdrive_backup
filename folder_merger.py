import shutil
import os
import argparse

from utils import folder_ops

parser = argparse.ArgumentParser()
parser.add_argument('--dry_run', action='store_true')
parser.add_argument('folders', nargs='+', type=str)
args = parser.parse_args()

for folder in args.folders:
    folder = os.path.abspath(folder)
    basename = os.path.basename(folder)
    if not basename.endswith('_split'):
        print("Refuse to merge this folder. It is not created by folder_splitter.py")
    
    part_list = folder_ops.get_folderlist_by_depth(folder, depth=1)
    target = folder[:-6]
    os.makedirs(target)

    for part in part_list:
        files = os.listdir(part)
        for fn in files:
            src = os.path.join(part, fn)
            if not args.dry_run:
                shutil.move(src, target)
            print("File:", src)
            print("To:", target)
