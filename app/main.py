import os
import re
import shutil
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile, WebSocket

from app import util

ACCEPTED_FILE_TYPES = ['audio/aiff', 'audio/mpeg', 'audio/wav', 'audio/vnd.dlna.adts', 'audio/ogg']
app = FastAPI()

if not os.path.exists(os.path.join(os.getcwd(), "tmp")):
    os.mkdir(os.path.join(os.getcwd(), "tmp"))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/separate")
async def separate_audio(file: UploadFile, background_tasks: BackgroundTasks):

    if file.content_type not in ACCEPTED_FILE_TYPES:
        raise HTTPException(status_code=415, detail="File must be an audio file in one of the following formats: (aac, aiff, mp3, ogg, wav)")

    clean_file_name = util.sanitize_filename(file.filename)
    checksum = await util.get_checksum(file)
    temp_file_path = os.path.join(os.getcwd(), "tmp", f"{checksum}_{clean_file_name}")

    await file.seek(0)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform source separation on the audio file
    background_tasks.add_task(util.separate_and_upload, checksum, clean_file_name, temp_file_path)

    return checksum
    

@app.get("/info")
async def get_info(id: str):
    return util.get_folder_details(id)