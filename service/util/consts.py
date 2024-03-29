import os.path

import torch

DEVICE = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
SEGMENT_STRIDE = 7.5
SEGMENT_DURATION = 15.0
REQUIRED_SAMPLE_RATE = 16000

LINGUISTIC_MODEL_EN_PATH = os.path.join("checkpoints", "linguistic_head_en.ckpt")
LINGUISTIC_MODEL_ZH_PATH = os.path.join("checkpoints", "linguistic_head_zh.ckpt")
AUDIO_MODEL_PATH = os.path.join("checkpoints", "audio_model_trill.pt")

LINGUISTIC_MODEL_ZH_URL = "https://github.com/ControlNet/emolysis/releases/download/misc/linguistic_head_zh.ckpt"
LINGUISTIC_MODEL_EN_URL = "https://github.com/ControlNet/emolysis/releases/download/misc/linguistic_head_en.ckpt"
AUDIO_MODEL_URL = "https://github.com/ControlNet/emolysis/releases/download/misc/audio_model_trill.pt"

COMMUNICATION_VISUAL_STEP = 100
COMMUNICATION_AUDIO_STEP = 10
COMMUNICATION_LINGUISTIC_STEP = 10
