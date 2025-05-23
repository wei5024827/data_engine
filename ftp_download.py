import os
import logging
from datetime import datetime
from ftplib import FTP

from utils import get_target_date
from db import fetch_download_patterns, record_download_result

def download_files(config):
    target_date = get_target_date()
    remote_dir = f"/data/crmpro/{target_date}"
    patterns = fetch_download_patterns(config)

    os.makedirs(config['local_dir'], exist_ok=True)

    ftp = FTP(config['agent_url'])
    ftp.login(config['agent_user'], config['pwd'])
    ftp.cwd(remote_dir)
    logging.info(f"Changed to remote directory: {remote_dir}")

    for pattern in patterns:
        logging.info(f"Processing pattern: {pattern}")
        try:
            files = ftp.nlst(pattern)
        except Exception as e:
            logging.error(f"No files found for pattern {pattern}: {e}")
            continue

        for filename in files:
            local_path = os.path.join(config['local_dir'], filename)
            try:
                remote_size = ftp.size(filename)
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {filename}', f.write)
                local_size = os.path.getsize(local_path)
                status = '1' if local_size == remote_size else '2'
            except Exception as e:
                logging.error(f"Download failed for {filename}: {e}")
                status = '2'

            finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            table_name = os.path.splitext(filename)[0]
            record_download_result(config, target_date, 'SRC_DPM', table_name, status, finish_time)

    ftp.quit()
