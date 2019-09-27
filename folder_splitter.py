import os
import sys
import queue
import argparse
import shutil

from utils import folder_ops

parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=int, default=750)
parser.add_argument('--dry_run', action='store_true')
parser.add_argument('paths', nargs='+', type=str)
args = parser.parse_args()

threshold_g = args.threshold

for folder_to_split in args.paths:
    folder_to_split = os.path.abspath(folder_to_split) # Convert to absolute path
    orig_size = folder_ops.get_size(folder_to_split)

    if os.path.isfile(folder_to_split):
        print("Cannot split a file")
        continue

    orig_size_g = orig_size / 1024.0 / 1024 / 1024
    if orig_size_g < threshold_g:
        print("No need to split")
        continue

    # Dry-run phase, do the analysis
    split_list = []
    cur_folder_list = [] # Current threshold_g G
    cur_size = 0
    folder_queue = queue.Queue()
    folder_queue.put(folder_to_split)
    while not folder_queue.empty():
        cur_work_dir = folder_queue.get()
        cur_work_dir_size_g = folder_ops.get_size(cur_work_dir) / 1024.0 / 1024 / 1024

        if cur_work_dir_size_g < threshold_g:
            if (cur_size + cur_work_dir_size_g) < threshold_g:
                cur_folder_list.append(cur_work_dir)
                cur_size += cur_work_dir_size_g
            else:
                split_list.append((cur_folder_list, cur_size))
                cur_folder_list = [cur_work_dir]
                cur_size = cur_work_dir_size_g
        else:
            subdir = folder_ops.get_folderlist_by_depth(cur_work_dir, depth=1)
            if len(subdir) == 0:
                # This is a file, and it is larger than threshold
                # It cannot be splitted
                print("Error, file", cur_work_dir, "is larger than 750G")
                continue
            else:
                for d in subdir:
                    folder_queue.put(d)
        
    
    if cur_size > 0:
        split_list.append((cur_folder_list, cur_size))

    # Create folder for move destination
    basename = os.path.basename(folder_to_split)
    new_root_path = os.path.join(os.path.dirname(folder_to_split), basename + '_split')

    for idx, (file_list, size) in enumerate(split_list):
        print("Folder:", idx)
        print("Size:", size, 'G')
        
        new_part_path = os.path.join(new_root_path, 'part_' + str(idx))
        if not args.dry_run:
            os.makedirs(new_part_path)

        for fn in file_list:
            rel_path = os.path.relpath(os.path.dirname(fn), folder_to_split)
            if rel_path != '.':
                # Not the direct subfolder of the folder_to_split
                # Need to create the structure
                subdir_struct = os.path.join(new_part_path, rel_path)
                if not args.dry_run:
                    os.makedirs(subdir_struct, exist_ok=True)
            dest_path = os.path.join(new_part_path, rel_path, os.path.basename(fn))
            if not args.dry_run:
                shutil.move(fn, dest_path)
            print("File:", fn)
            print("To:", dest_path)

