import subprocess
import sys
import os
import configparser
import math
import shutil

from utils import folder_ops
from utils import executor

# Usage: python main.py <TorrentID> <Content folder name>

def main():
    if not os.path.exists('./config.ini'):
        print("Please run bootstrap.py first")
        raise FileNotFoundError
    config = configparser.ConfigParser()
    config.read('./config.ini')

    torrent_id = sys.argv[1]
    folder_name = sys.argv[2]
    base_working_dir = config['misc']['prefix']
    rel_content_path = os.path.join('./', folder_name)
    abs_content_path = os.path.join(base_working_dir, folder_name)
    rel_backup_path = os.path.join('./', 'backup')
    abs_backup_path = os.path.join(base_working_dir, 'backup')

    # Compress folder
    os.makedirs(abs_backup_path, exist_ok=True)
    rar_cmd = [config['toolchain']['rar'], 'a']
    rar_cmd.append('-v' + config['rar']['split']) # Splitted volume
    rar_cmd += ['-m1', '-ma5', '-md128m', '-s']
    rar_cmd.append('-rr' + config['rar']['rr']) # Recovery record percentage
    rar_cmd.append(os.path.join(rel_backup_path, folder_name + '.rar')) # RAR file path
    rar_cmd.append(rel_content_path)
    
    executor.execute(rar_cmd, working_dir=base_working_dir)

    # par2 verify
    rar_volume_size = folder_ops.get_size(abs_backup_path)
    bs_scale_factor = max(60 * 1024 * 1024 * 1024 / float(rar_volume_size), 1.0) # 1GB/block, 2 backup files with 3 blocks each as reference; therefore, scale the block size to reach this reference
    block_size = int(int(config['par2']['block']) / bs_scale_factor)
    if block_size % 4 != 0:
        # Block size must be a multiple of 4
        block_size += 4 - (block_size % 4)
    block_count = math.ceil(float(rar_volume_size) / block_size)
    backup_block_count = math.ceil(block_count * int(config['par2']['redundancy']) / 100.0)
    par2_volume_count = math.ceil(backup_block_count / 3.0)

    par2_cmd = [config['toolchain']['par2'], 'c']
    par2_cmd.append('-s' + str(block_size)) # block size
    par2_cmd.append('-r' + config['par2']['redundancy']) # redundancy percentage
    par2_cmd.append('-u')
    par2_cmd.append('-m' + config['par2']['memory']) # memory limit
    par2_cmd.append('-v')
    par2_cmd.append('-n' + str(par2_volume_count))
    par2_cmd.append(os.path.join('./', folder_name + '.rar.par2'))
    par2_cmd.append(os.path.join('./', folder_name + '.part*.rar'))

    executor.execute(par2_cmd, working_dir=abs_backup_path)

    # rclone upload
    raw_folder_cmd = [config['toolchain']['rclone'], 'copy', abs_content_path]
    raw_folder_cmd.append(config['rclone']['raw_account'] + ':/' + torrent_id + '/' + folder_name)
    raw_folder_cmd += ['-v', '--transfers', '12', '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36']
    
    executor.execute(raw_folder_cmd)

    backup_cmd = [config['toolchain']['rclone'], 'copy', abs_backup_path]
    backup_cmd.append(config['rclone']['compress_account'] + ':/' + torrent_id + '/backup')
    backup_cmd += ['-v', '--transfers', '12', '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36']

    executor.execute(backup_cmd)

    full_path_size = folder_ops.get_size(abs_content_path) / 1024.0 / 1024 / 1024
    backup_size = folder_ops.get_size(abs_backup_path) / 1024.0 / 1024 / 1024
    max_size = max(full_path_size, backup_size)
    print("Quota usage:", max_size, 'GB')

    shutil.rmtree(abs_backup_path)

if __name__ == "__main__":
    main() 
    
    


