import shutil
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('folders', )


source = '/path/to/source_folder'
dest1 = '/path/to/dest_folder'


files = os.listdir(source)

for f in files:
        shutil.move(source+f, dest1)