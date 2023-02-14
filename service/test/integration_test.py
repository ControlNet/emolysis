import asyncio
import argparse
from pathlib import Path

from starlette.websockets import WebSocket


from gen_audio_result import process_audio_file
from gen_text_result import process_text_file
from gen_visual_result import process_video_file
from model.text2speech import text2speech


class FakeWebSocket(WebSocket):

    def __init__(self):
        pass

    async def send_json(self, data, mode="text"):
        pass

    async def receive_text(self):
        return "ok"


socket = FakeWebSocket()


async def process_uploaded(video_path: str, lang: str):
    video_dir = Path(video_path).parent
    text2speech_path = str(video_dir / "text2speech.json")
    audio_result_path = str(video_dir / "audio.csv")
    text_result_path = str(video_dir / "text.csv")
    visual_result_path = str(video_dir / "faces.csv")

    text2speech(video_path, text2speech_path, lang)
    await process_audio_file(video_path, audio_result_path, socket)
    await process_text_file(text2speech_path, text_result_path, lang, socket)
    await process_video_file(video_path, visual_result_path, socket)

    return {
        "id": video_dir.name,
        "audio": audio_result_path.replace("\\", "/"),
        "visual": visual_result_path.replace("\\", "/"),
        "text": text_result_path.replace("\\", "/"),
    }


parser = argparse.ArgumentParser()
parser.add_argument("--video_path", type=str)
parser.add_argument("--lang", type=str)

if __name__ == '__main__':
    args = parser.parse_args()
    asyncio.run(process_uploaded(args.video_path, args.lang))
