import os
import re
import shutil
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
import yt_dlp
from app import util
from fastapi.responses import FileResponse

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
    

@app.get("/ytdl")
async def download_youtube(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'paths': {
            'home': './ytdl'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        filename = os.path.splitext(ydl.prepare_filename(info))[0]
    
    return FileResponse(f"{filename}.mp3")

@app.get("/info")
async def get_info(id: str):
    return util.get_folder_details(id)