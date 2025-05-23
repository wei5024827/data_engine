import logging
from config import load_config
from ftp_download import download_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    config = load_config()
    download_files(config)
