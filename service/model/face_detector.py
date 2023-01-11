from facenet_pytorch.models.mtcnn import MTCNN

from util.consts import DEVICE

mtcnn = MTCNN(keep_all=False, post_process=False,
    min_face_size=40, device=DEVICE)


def detect_face(frame, threshold=0.9):
    bounding_boxes, probs = mtcnn.detect(frame, landmarks=False)
    if bounding_boxes is not None:
        return bounding_boxes[probs > threshold], probs
    else:
        return [], None
