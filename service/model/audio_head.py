import tensorflow_hub as hub
import torch
from torch import nn
from torch.nn import functional as F

from util.consts import DEVICE, AUDIO_MODEL_PATH


class AudioDnn(nn.Module):

    def __init__(self):
        super(AudioDnn, self).__init__()
        self.fc1 = nn.Linear(512, 1024)
        self.fc2 = nn.Linear(1024, 2048)
        self.fc3 = nn.Linear(2048, 4096)
        self.fc4_cont = nn.Linear(4096, 3)
        self.fc4_dis = nn.Linear(4096, 26)
        self.dropout = nn.Dropout(0.3)
        self.bn1 = nn.BatchNorm1d(1024)
        self.bn2 = nn.BatchNorm1d(2048)
        self.bn3 = nn.BatchNorm1d(4096)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = F.relu(self.bn3(self.fc3(x)))
        x_pen = self.dropout(x)
        x_dis = self.fc4_dis(x_pen)
        x_dis = x_dis.sigmoid()  # sigmoid activation to get logits for emotion
        x_cont = self.fc4_cont(x_pen)  # valence, arousal and dominance
        return x_dis, x_cont, x_pen


_module = None


def get_trill_model():
    global _module
    if _module is None:
        import tensorflow as tf
        for device in tf.config.experimental.list_physical_devices('GPU'):
            tf.config.experimental.set_virtual_device_configuration(device,
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=3500)])

        _module = hub.load('https://tfhub.dev/google/nonsemantic-speech-benchmark/trill/3')
    return _module


def get_audio_model():
    checkpoint = torch.load(AUDIO_MODEL_PATH, map_location=DEVICE)
    model = AudioDnn()
    model.load_state_dict(checkpoint)
    model = model.to(DEVICE)
    model.eval()
    return model
