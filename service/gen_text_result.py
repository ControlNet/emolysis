import json
import pathlib

import pandas as pd
from starlette.websockets import WebSocket

from model.linguistic_head import get_tokenizer_zh, get_linguistic_model_zh, get_tokenizer_en, predict_emotion_en, \
    get_linguistic_model_en
from util.consts import DEVICE, COMMUNICATION_LINGUISTIC_STEP
from util.label_space_mapping import bold_to_main, bold_to_main_valence, bold_to_main_arousal


def get_results_from_text_zh(msg):
    tokenizer = get_tokenizer_zh()
    tokenized_text = tokenizer([msg], return_tensors="pt", padding=True)
    linguistic_model = get_linguistic_model_zh()
    tokenized_text = tokenized_text.to(DEVICE)
    if tokenized_text["input_ids"].shape[1] > 512:
        tokenized_text["input_ids"] = tokenized_text["input_ids"][:, :512]
        tokenized_text["token_type_ids"] = tokenized_text["token_type_ids"][:, :512]
        tokenized_text["attention_mask"] = tokenized_text["attention_mask"][:, :512]
    output_valence, output_arousal, output_emo, _ = linguistic_model(tokenized_text)

    output_emo = output_emo.cpu().detach().numpy()
    output_valence = output_valence.cpu().detach().numpy()
    output_arousal = output_arousal.cpu().detach().numpy()

    # Mapping linguistic outputs to main label space
    main_linguistic_emo_prob = bold_to_main(output_emo[0])
    main_linguistic_valence = bold_to_main_valence(output_valence[0])
    main_linguistic_arousal = bold_to_main_arousal(output_arousal[0])

    return main_linguistic_emo_prob, main_linguistic_valence, main_linguistic_arousal


def get_results_from_text_en(msg):
    tokenizer = get_tokenizer_en()
    tokenized_text = tokenizer([msg], return_tensors="pt", padding=True)
    linguistic_model = get_linguistic_model_en()
    tokenized_text = tokenized_text.to(DEVICE)
    if tokenized_text["input_ids"].shape[1] > 512:
        tokenized_text["input_ids"] = tokenized_text["input_ids"][:, :512]
        tokenized_text["token_type_ids"] = tokenized_text["token_type_ids"][:, :512]
        tokenized_text["attention_mask"] = tokenized_text["attention_mask"][:, :512]
    output_valence, output_arousal = linguistic_model(tokenized_text)

    output_valence = output_valence.cpu().detach().numpy()[0, 0]
    output_arousal = output_arousal.cpu().detach().numpy()[0, 0]

    # Mapping linguistic outputs to main label space
    main_linguistic_valence = output_valence * 1000
    main_linguistic_arousal = output_arousal * 1000
    main_linguistic_emo_prob = predict_emotion_en(msg)

    return main_linguistic_emo_prob, main_linguistic_valence, main_linguistic_arousal


def get_results_with_lang(lang):
    if lang == "zh":
        return get_results_from_text_zh
    elif lang == "en":
        return get_results_from_text_en
    else:
        raise ValueError("Language not supported")


async def process_text_file(file_path: str, result_path: str, lang: str, socket: WebSocket):
    with open(file_path, "r", encoding="UTF-8") as f:
        input_text = json.load(f)

    df = []

    total = len(input_text["segments"])

    for (i, segment) in enumerate(input_text["segments"]):
        start = segment["start"]
        end = segment["end"]
        msg = segment["text"].strip()
        # pass msg to text model
        main_linguistic_emo_prob, main_linguistic_valence, main_linguistic_arousal = get_results_with_lang(lang)(msg)
        main_linguistic_emo_prob = main_linguistic_emo_prob / main_linguistic_emo_prob.sum()
        df.append({
            "start": start,
            "end": end,
            "valence": main_linguistic_valence,
            "arousal": main_linguistic_arousal,
            "emotion0": main_linguistic_emo_prob[0],
            "emotion1": main_linguistic_emo_prob[1],
            "emotion2": main_linguistic_emo_prob[2],
            "emotion3": main_linguistic_emo_prob[3],
            "emotion4": main_linguistic_emo_prob[4],
            "emotion5": main_linguistic_emo_prob[5],
            "emotion6": main_linguistic_emo_prob[6],
            "emotion7": main_linguistic_emo_prob[7],
            "emotion8": main_linguistic_emo_prob[8],
        })

        # if (i + 1) % COMMUNICATION_LINGUISTIC_STEP == 0:
        #     await socket.send_json({"status": "text", "data": {"current": i, "total": total}})
        #     await socket.receive_text()

    pathlib.Path(result_path).parent.mkdir(exist_ok=True, parents=True)
    pd.DataFrame(df).to_csv(result_path, index=False)
    print(f"[Linguistic Head] Process {pathlib.Path(file_path).parent.name}")
