import pathlib
from collections import OrderedDict

import librosa
import numpy as np
import pandas as pd
import torch
from pydub import AudioSegment
from starlette.websockets import WebSocket
from torch.autograd import Variable

from model.audio_head import get_audio_model, get_trill_model
from util.consts import DEVICE, SEGMENT_STRIDE, SEGMENT_DURATION, REQUIRED_SAMPLE_RATE, COMMUNICATION_AUDIO_STEP
from util.label_space_mapping import bold_to_main, bold_to_main_valence, bold_to_main_arousal


def get_emotion_features_from_audio(audio, original_sample_rate):
    audio_model = get_audio_model()
    features = extract_trill_features(audio, original_sample_rate)

    with torch.no_grad():
        features = Variable(features).to(DEVICE)
        output_dis, output_con, output_feat = audio_model(features.float())

        output_emo = output_dis.cpu().detach().numpy()
        output_con = output_con.cpu().detach().numpy()
        output_valence = output_con[:, 0]
        output_arousal = output_con[:, 1]
        pen_features = output_feat.cpu().detach().numpy()

        return output_valence, output_arousal, output_emo, pen_features


def extract_trill_features(audio, original_sample_rate):
    module = get_trill_model()
    float_audio = audio.astype(np.float32) / np.iinfo(np.int16).max
    if original_sample_rate != REQUIRED_SAMPLE_RATE:
        float_audio = librosa.core.resample(
            float_audio.T, orig_sr=original_sample_rate, target_sr=REQUIRED_SAMPLE_RATE,
            res_type='kaiser_best')
    float_audio = float_audio.flatten()
    emb_dict = module(samples=float_audio, sample_rate=16000)
    emb = emb_dict['embedding']
    emb.shape.assert_is_compatible_with([None, 512])
    feat = np.average(emb, axis=0)
    feat = torch.as_tensor(np.array(feat).astype('float'))
    # add a dimension to act as batch dimension
    feat = torch.unsqueeze(feat, 0)
    return feat


async def process_audio_file(file_path: str, result_path: str, socket: WebSocket):
    clip = AudioSegment.from_file(file_path)
    orig_sampling_rate = clip.frame_rate

    data = OrderedDict()

    arange_iter = np.arange(0.0, clip.duration_seconds, SEGMENT_STRIDE)

    for (n, i) in enumerate(arange_iter):
        start_time = int(i * 1000)
        end_time = int(min(i + SEGMENT_DURATION, clip.duration_seconds) * 1000)

        segment = clip[start_time:end_time]
        # pass audio segment to audio based model
        # get ndarray from AudioSegment object
        audio_array = np.array(segment.get_array_of_samples())
        audio_features = get_emotion_features_from_audio(audio_array, orig_sampling_rate)
        audio_valence, audio_arousal, audio_emotion, _ = audio_features

        # Mapping audio outputs to the main label space
        main_audio_emo_prob = bold_to_main(audio_emotion[0])
        main_audio_valence = bold_to_main_valence(audio_valence[0])
        main_audio_arousal = bold_to_main_arousal(audio_arousal[0])
        result = np.array([main_audio_arousal, main_audio_valence, *main_audio_emo_prob])

        start_time = start_time / 1000
        end_time = end_time / 1000
        mid_time = start_time + SEGMENT_STRIDE
        if mid_time < clip.duration_seconds:
            if (start_time, mid_time) in data:
                data[(start_time, mid_time)].append(result)
            else:
                data[(start_time, mid_time)] = [result]

            if (mid_time, end_time) in data:
                data[(mid_time, end_time)].append(result)
            else:
                data[(mid_time, end_time)] = [result]
        else:
            if (start_time, end_time) in data:
                data[(start_time, end_time)].append(result)
            else:
                data[(start_time, end_time)] = [result]

        if (n + 1) % COMMUNICATION_AUDIO_STEP == 0:
            await socket.send_json({"status": "audio", "data": {"current": n, "total": len(arange_iter)}})
            await socket.receive_text()

    df = []

    for key, value in data.items():
        value = np.stack(value, axis=0).mean(axis=0)
        value[2:] = value[2:] / value[2:].sum()
        df.append({
            "start": key[0],
            "end": key[1],
            "valence": value[1],
            "arousal": value[0],
            "emotion0": value[2],
            "emotion1": value[3],
            "emotion2": value[4],
            "emotion3": value[5],
            "emotion4": value[6],
            "emotion5": value[7],
            "emotion6": value[8],
            "emotion7": value[9],
            "emotion8": value[10],
        })

    pathlib.Path(result_path).parent.mkdir(exist_ok=True, parents=True)
    pd.DataFrame(df).to_csv(result_path, index=False)
    print(f"[Audio Head] Process {pathlib.Path(file_path).parent.name}")
