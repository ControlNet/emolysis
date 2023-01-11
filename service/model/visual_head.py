from hsemotion.facial_emotions import HSEmotionRecognizer

from util.consts import DEVICE


def predict_emotions(model, face_img):
    emotion, scores = model.predict_emotions(face_img, logits=False)
    return emotion, scores


def emotion_VA_MTL(device):
    model_name = 'enet_b0_8_va_mtl'
    fer = HSEmotionRecognizer(model_name=model_name, device=device)
    return fer


_video_model = None


def get_video_model():
    global _video_model
    if _video_model is None:
        _video_model = emotion_VA_MTL(DEVICE)
    return _video_model
