import whisper
import json
import pathlib

_model = None


def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def text2speech(file_path: str, output_path: str):
    model = get_model()
    result = model.transcribe(file_path, language="en")

    pathlib.Path(output_path).parent.mkdir(exist_ok=True, parents=True)
    with open(output_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"[text2speech] Process {pathlib.Path(file_path).parent.name}")
