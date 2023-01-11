import pathlib
from math import ceil

import numpy as np
import pandas as pd
from moviepy.editor import VideoFileClip
from starlette.websockets import WebSocket
from tqdm.auto import tqdm

from model.face_detector import detect_face
from model.visual_head import predict_emotions, get_video_model
from util.consts import COMMUNICATION_VISUAL_STEP
from util.label_space_mapping import affectnet_to_main, affectnet_to_main_valence, affectnet_to_main_arousal


async def process_video_file(file_path: str, result_path: str, socket: WebSocket):

    video_model = get_video_model()

    with VideoFileClip(file_path) as clip:
        results = []
        total = ceil(clip.fps * clip.duration)

        await socket.send_json({"status": "visual start", "data": {"fps": clip.fps}})
        await socket.receive_text()

        for i, frame in enumerate(tqdm(clip.iter_frames(), total=total)):
            try:
                bounding_boxes, probs = detect_face(frame)

                for j, bbox in enumerate(bounding_boxes):
                    prob = probs[j]
                    box = bbox.astype(int)
                    x1, y1, x2, y2 = box[0:4]
                    face_img = frame[max(0, y1):y2, max(0, x1):x2]
                    if len(face_img) != 0:
                        _, scores = predict_emotions(video_model, face_img)
                        valance = scores[8]
                        arousal = scores[9]

                        emotion_prob = affectnet_to_main(scores)

                        valance = int(affectnet_to_main_valence(valance))
                        arousal = int(affectnet_to_main_arousal(arousal))

                        emotion_prob = emotion_prob / np.sum(emotion_prob)

                        results.append({
                            "frame": i,
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                            "box_prob": prob,
                            "emotion0": emotion_prob[0],
                            "emotion1": emotion_prob[1],
                            "emotion2": emotion_prob[2],
                            "emotion3": emotion_prob[3],
                            "emotion4": emotion_prob[4],
                            "emotion5": emotion_prob[5],
                            "emotion6": emotion_prob[6],
                            "emotion7": emotion_prob[7],
                            "emotion8": emotion_prob[8],
                            "valence": valance,
                            "arousal": arousal,
                        })
                    else:
                        print(i, ":", "No face")
            except Exception as e:
                raise e

            if (i + 1) % COMMUNICATION_VISUAL_STEP == 0:
                await socket.send_json({"status": "visual", "data": {"current": i, "total": total}})
                await socket.receive_text()

    pathlib.Path(result_path).parent.mkdir(exist_ok=True, parents=True)
    pd.DataFrame(results).to_csv(result_path, index=False, sep=",")
    print(f"[Visual Head] Process {pathlib.Path(file_path).parent.name}")
