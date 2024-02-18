from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
import aiofile
from config import tmp
from starlette.responses import FileResponse
import zipfile

from make_file import make_file_from

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return tmp.TemplateResponse("index.html", {"request": request})

@app.post("/file/load")
async def main_page(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File is not .zip")

    path_to_zip = f"zip_folder/{file.filename}"
    path_to_xlsx = f"file/{file.filename.replace('.zip', '.xlsx')}"

    async with aiofile.async_open(path_to_zip, "wb") as afile:
        await afile.write(await file.read())

    make_file_from(path_to_zip, path_to_xlsx)

    return FileResponse(path_to_xlsx, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file.filename.replace('.zip', '.xlsx'))
