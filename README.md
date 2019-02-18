# gdrive_backup
Automatically backup torrent contents (like U2) to google drive, including raw folder upload and PAR2-verified RAR volume.

## Usage
Run `bootstrap.py` first, which creates `config.ini`. You can also write it by hand according to `config_example.ini`

Backup command:
```
python3 main.py <TorrentID> <FolderName>
```
