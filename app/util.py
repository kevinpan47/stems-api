

import datetime
import hashlib
import os
import re
import shutil
from demucs import separate
from fastapi import UploadFile
from google.cloud import storage

credentials_json_file = os.path.join(os.getcwd(), './service-account-key.json')
client = storage.Client.from_service_account_json(credentials_json_file)
bucket = client.get_bucket('stems-split')


async def get_checksum(file: UploadFile):
    checksum = hashlib.sha256()

    # Read the file in chunks and update the checksum
    while chunk := await file.read(8192):  # Adjust the chunk size as needed
        checksum.update(chunk)

    # Get the hexadecimal representation of the checksum
    checksum_value = checksum.hexdigest()

    return checksum_value


def sanitize_filename(filename: str):
    # Remove invalid characters
    cleaned_filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Remove leading and trailing spaces
    cleaned_filename = cleaned_filename.strip()

    # Replace consecutive spaces with a single space
    cleaned_filename = re.sub(r'\s+', ' ', cleaned_filename)

    # Replace remaining spaces with underscores
    cleaned_filename = cleaned_filename.replace(' ', '_')

    return cleaned_filename


def separate_and_upload(checksum: str, src_file_name: str, src_file_path: str):
    try:
        separate.main(["--mp3", "-d", "cpu", src_file_path])
    except:
        print('could not process file')
    
    blob = bucket.blob(f'{checksum}/{src_file_name}')
    blob.upload_from_filename(src_file_path)

    for filename in os.scandir(os.path.join(os.getcwd(), 'separated', 'htdemucs', os.path.splitext(os.path.basename(src_file_path))[0])):
        if filename.is_file():
            print(filename.path)
            blob = bucket.blob(f'{checksum}/{os.path.splitext(src_file_name)[0]}_{filename.name}')
            blob.upload_from_filename(filename.path)
    
    # cleanup
    shutil.rmtree(os.path.join(os.getcwd(), 'separated', 'htdemucs', os.path.splitext(os.path.basename(src_file_path))[0]))
    os.unlink(src_file_path)


def get_folder_details(id: str):
    details = {'id': id}

    blobs = client.list_blobs('stems-split', prefix=id, delimiter='/')
    for blob in blobs:
        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=datetime.timedelta(minutes=5),
            # Allow GET requests using this URL.
            method="GET",
        )
        details[os.path.basename(blob.name)] = url
    
    return details