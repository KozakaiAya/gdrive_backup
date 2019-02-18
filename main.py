import subprocess
import sys
import os
import configparser
import math
import shutil

# Usage: python main.py <TorrentID> <Content folder name>

def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def execute(command):
    print("Executing:", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().decode(sys.stdout.encoding)
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output

def main():
    if not os.path.exists('./config.ini'):
        print("Please run bootstrap.py first")
        raise FileNotFoundError
    config = configparser.ConfigParser()
    config.read('./config.ini')

    torrent_id = int(sys.argv[1])
    folder_name = sys.argv[2]
    full_content_path = os.path.join(config['misc']['prefix'], folder_name)
    backup_path = os.path.join(config['misc']['prefix'], 'backup')

    # Compress folder
    os.makedirs(backup_path, exist_ok=True)
    rar_cmd = [config['toolchain']['rar'], 'a']
    rar_cmd.append('-v' + config['rar']['split']) # Splitted volume
    rar_cmd += ['-m1', '-ma5', '-md128m', '-s']
    rar_cmd.append('-rr' + config['rar']['rr']) # Recovery record percentage
    rar_cmd.append(os.path.join(backup_path, folder_name + '.rar')) # RAR file path
    rar_cmd.append(full_content_path)
    
    execute(rar_cmd)

    # par2 verify
    rar_volume_size = get_size(backup_path)
    block_count = math.ceil(float(rar_volume_size) / int(config['par2']['block']))
    backup_block_count = math.ceil(block_count * int(config['par2']['redundancy']) / 100.0)
    par2_volume_count = math.ceil(backup_block_count / 3.0)

    par2_cmd = [config['toolchain']['par2'], 'c']
    par2_cmd.append('-s' + config['par2']['block']) # block size
    par2_cmd.append('-r' + config['par2']['redundancy']) # redundancy percentage
    par2_cmd.append('-u')
    par2_cmd.append('-m' + config['par2']['memory']) # memory limit
    par2_cmd.append('-v')
    par2_cmd.append('-n' + str(par2_volume_count))
    par2_cmd.append(os.path.join(backup_path, folder_name + '.rar.par2'))
    par2_cmd.append(config['misc']['prefix'] + '/backup/' + folder_name + '.part*.rar')

    execute(par2_cmd)

    # rclone upload
    raw_folder_cmd = [config['toolchain']['rclone'], 'copy', full_content_path]
    raw_folder_cmd.append(config['rclone']['raw_account'] + ':/' + torrent_id + '/' + folder_name)
    
    execute(raw_folder_cmd)

    backup_cmd = [config['toolchain']['rclone'], 'copy', backup_path]
    backup_cmd.append(config['rclone']['raw_account'] + ':/' + torrent_id + '/backup')

    execute(backup_cmd)

    full_path_size = get_size(full_content_path) / 1024.0 / 1024 / 1024
    backup_path = get_size(backup_path) / 1024.0 / 1024 / 1024
    max_size = max(full_path_size, backup_path)
    print("Quota usage:", max_size, 'GB')

    shutil.rmtree(backup_path)

if __name__ == "__main__":
    main() 
    
    


