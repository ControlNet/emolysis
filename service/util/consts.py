import os.path

import torch

DEVICE = torch.device("cuda:0")
SEGMENT_STRIDE = 7.5
SEGMENT_DURATION = 15.0
REQUIRED_SAMPLE_RATE = 16000

LINGUISTIC_MODEL_EN_PATH = os.path.join("checkpoints", "linguistic_head_en.ckpt")
LINGUISTIC_MODEL_ZH_PATH = os.path.join("checkpoints", "linguistic_head_zh.ckpt")
AUDIO_MODEL_PATH = os.path.join("checkpoints", "audio_model_trill.pt")

LINGUISTIC_MODEL_ZH_URL = None
LINGUISTIC_MODEL_EN_URL = None
AUDIO_MODEL_URL = None

COMMUNICATION_VISUAL_STEP = 100
COMMUNICATION_AUDIO_STEP = 10
COMMUNICATION_LINGUISTIC_STEP = 10
