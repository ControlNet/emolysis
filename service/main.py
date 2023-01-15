import warnings
from pathlib import Path

import uvicorn
from fastapi import FastAPI, UploadFile
from moviepy.video.io.VideoFileClip import VideoFileClip
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.websockets import WebSocket

from gen_audio_result import process_audio_file
from gen_text_result import process_text_file
from gen_visual_result import process_video_file
from model.text2speech import text2speech
from util.misc import VideoNamePool, range_requests_response, prepare_checkpoints

warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VideoNamePool.init()
prepare_checkpoints()


@app.get("/data/{video_id}/{file_name}")
async def get_file(video_id: str, file_name: str, request: Request):
    path = str(Path("data") / video_id / file_name)
    if file_name.split(".")[-1] == "mp4":
        return range_requests_response(
            request, file_path=path, content_type="video/mp4"
        )
    else:
        return FileResponse(
            path=path, media_type="text"
        )


async def process_uploaded(video_path: str, lang: str, socket: WebSocket):
    video_dir = Path(video_path).parent
    text2speech_path = str(video_dir / "text2speech.json")
    audio_result_path = str(video_dir / "audio.csv")
    text_result_path = str(video_dir / "text.csv")
    visual_result_path = str(video_dir / "faces.csv")

    text2speech(video_path, text2speech_path, lang)
    await process_audio_file(video_path, audio_result_path, socket)
    await socket.send_json({"status": "audio done", "data": {}})
    await socket.receive_text()

    await process_text_file(text2speech_path, text_result_path, lang, socket)
    await socket.send_json({"status": "text done", "data": {}})
    await socket.receive_text()

    await process_video_file(video_path, visual_result_path, socket)
    await socket.send_json({"status": "visual done", "data": {}})
    await socket.receive_text()

    return {
        "id": video_dir.name,
        "audio": audio_result_path.replace("\\", "/"),
        "visual": visual_result_path.replace("\\", "/"),
        "text": text_result_path.replace("\\", "/"),
    }


@app.post("/upload")
async def upload_video(file: UploadFile):
    file_id = VideoNamePool.get()
    path = Path(f"data/{file_id}")
    video_path = str(path / "video.mp4")
    path.mkdir(exist_ok=True, parents=True)
    with open(video_path, "wb") as f:
        f.write(await file.read())
    return {"file_id": file_id}


@app.get("/fps/{video_id}")
async def get_fps(video_id: str):
    video_path = Path(f"data/{video_id}/video.mp4")
    with VideoFileClip(str(video_path)) as video:
        fps = video.fps
        return {"fps": fps}


@app.websocket("/")
async def socket_connection(socket: WebSocket):
    await socket.accept()
    video_info = await socket.receive_json()
    file_id = video_info["file_id"]
    lang = video_info["lang"]
    video_path = str(Path("data") / str(file_id) / "video.mp4")

    await socket.send_json({"status": "uploaded", "data": {}})
    await socket.receive_text()
    result_paths = await process_uploaded(video_path, lang, socket)
    await socket.send_json({"status": "done", "data": result_paths})
    await socket.close()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=16000)
