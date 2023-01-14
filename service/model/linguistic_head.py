from typing import Dict, Tuple, Optional, Union, Sequence

import numpy as np
import torch
from tensorneko import NekoModel
from tensorneko.layer import Linear
from torch import Tensor
from torch.nn import ReLU, CrossEntropyLoss, BCEWithLogitsLoss, MSELoss
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from transformers import BertModel, BertTokenizer, pipeline, RobertaTokenizer, RobertaModel

from util.consts import LINGUISTIC_MODEL_ZH_PATH, DEVICE, LINGUISTIC_MODEL_EN_PATH


# English model

class LinguisticHeadEn(NekoModel):

    def __init__(self, learning_rate: float = 1e-5, finetune: bool = False):
        super().__init__("linguistic_head_en")
        self.roberta = get_roberta_en()
        self.hidden_fc = Linear(768, 1024, build_activation=ReLU)
        self.valence_fc = Linear(1024, 1)
        self.arousal_fc = Linear(1024, 1)
        self.finetune = finetune

        self.valence_loss_fn = MSELoss()
        self.arousal_loss_fn = MSELoss()
        self.learning_rate = learning_rate

    def forward(self, x: Dict[str, Tensor]) -> Tuple[Tensor, Tensor]:
        if not self.finetune:
            self.roberta.eval()
            with torch.no_grad():
                features = self.roberta(**x).pooler_output
        else:
            self.roberta.train()
            features = self.roberta(**x).pooler_output

        hidden = self.hidden_fc(features)
        pred_valence = self.valence_fc(hidden)
        pred_arousal = self.arousal_fc(hidden)
        return pred_valence, pred_arousal

    def step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]]):
        x, y_valence, y_arousal = batch
        pred_valence, pred_arousal = self(x)

        results = {}
        v_loss = self.valence_loss_fn(pred_valence, y_valence)
        a_loss = self.arousal_loss_fn(pred_arousal, y_arousal)
        loss = v_loss + a_loss
        results["loss"] = loss
        results["v_loss"] = v_loss
        results["a_loss"] = a_loss

        return results

    def training_step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]] = None, batch_idx: Optional[int] = None,
        optimizer_idx: Optional[int] = None, hiddens: Optional[Tensor] = None
    ) -> Dict[str, Tensor]:
        return self.step(batch)

    def validation_step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]] = None, batch_idx: Optional[int] = None,
        dataloader_idx: Optional[int] = None
    ) -> Dict[str, Tensor]:
        return self.step(batch)

    def configure_optimizers(self):
        optimizer = Adam(self.parameters(), lr=self.learning_rate, betas=(0.5, 0.9))
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": ReduceLROnPlateau(optimizer, factor=0.5, patience=10, verbose=True, min_lr=1e-8),
                "monitor": "val_loss"
            }
        }


_roberta_en: Optional[BertModel] = None
_tokenizer_en: Optional[BertTokenizer] = None
_emotion_model_en: Optional[pipeline] = None


def get_roberta_en() -> BertModel:
    global _roberta_en
    if _roberta_en is None:
        _roberta_en = RobertaModel.from_pretrained("roberta-base")
    return _roberta_en


def get_emotion_model_en():
    global _emotion_model_en
    if _emotion_model_en is None:
        _emotion_model_en = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
            top_k=7)
    return _emotion_model_en


def predict_emotion_en(text: str):
    emo_prob = np.zeros(9)
    model = get_emotion_model_en()
    result = model(text)
    for item in result[0]:
        if item["label"] == "joy":
            emo_prob[2] = item["score"]
        elif item["label"] == "surprise":
            emo_prob[5] = item["score"]
        elif item["label"] == "neutral":
            emo_prob[8] = item["score"]
        elif item["label"] == "anger":
            emo_prob[1] = item["score"]
        elif item["label"] == "sadness":
            emo_prob[3] = item["score"]
        elif item["label"] == "disgust":
            emo_prob[4] = item["score"]
        elif item["label"] == "fear":
            emo_prob[0] = item["score"]
        else:
            raise ValueError("Unknown emotion")
    return emo_prob


def get_tokenizer_en() -> BertTokenizer:
    global _tokenizer_en
    if _tokenizer_en is None:
        _tokenizer_en = RobertaTokenizer.from_pretrained("roberta-base")
    return _tokenizer_en


_linguistic_model_en = None


def get_linguistic_model_en() -> LinguisticHeadEn:
    global _linguistic_model_en
    if _linguistic_model_en is None:
        _linguistic_model_en = LinguisticHeadEn(finetune=False).load_from_checkpoint(LINGUISTIC_MODEL_EN_PATH,
            strict=False, map_location=DEVICE)
        _linguistic_model_en = _linguistic_model_en.to(DEVICE)

    return _linguistic_model_en



# Chinese model

class LinguisticHeadZh(NekoModel):

    def __init__(self, learning_rate: float = 1e-5, finetune: bool = False):
        super().__init__("linguistic_head_zh")
        self.roberta = get_roberta_zh()
        self.hidden_fc = Linear(1024, 1024, build_activation=ReLU)
        self.sentiment_classifier = Linear(1024, 3)
        self.emotion_classifier = Linear(1024, 26)
        self.valence_fc = Linear(1024, 1)
        self.arousal_fc = Linear(1024, 1)
        self.finetune = finetune

        self.sentiment_loss_fn = CrossEntropyLoss()
        self.emotion_loss_fn = BCEWithLogitsLoss()
        self.valence_loss_fn = MSELoss()
        self.arousal_loss_fn = MSELoss()
        self.learning_rate = learning_rate

    def forward(self, x: Dict[str, Tensor]) -> Tuple[Tensor, Tensor, Tensor, Tensor]:
        if not self.finetune:
            self.roberta.eval()
            with torch.no_grad():
                features = self.roberta(**x).pooler_output
        else:
            self.roberta.train()
            features = self.roberta(**x).pooler_output

        hidden = self.hidden_fc(features)
        pred_emotion = self.emotion_classifier(hidden)
        pred_emotion = pred_emotion.softmax(dim=1)
        pred_valence = self.valence_fc(hidden)
        pred_arousal = self.arousal_fc(hidden)
        return pred_valence, pred_arousal, pred_emotion, hidden

    def step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]]):
        x, y_sentiment, y_emotion, y_valence, y_arousal = batch
        pred_sentiment, pred_emotion, pred_valence, pred_arousal = self(x)

        results = {}

        if y_sentiment is not None:
            pred_sentiment = pred_sentiment.softmax(dim=1)
            results["s_loss"] = self.sentiment_loss_fn(
                pred_sentiment, y_sentiment)
            results["s_acc"] = self._s_acc_fn(pred_sentiment, y_sentiment)
            results["loss"] = results["s_loss"]

        elif y_emotion is not None and y_valence is not None and y_arousal is not None:
            pred_emotion = pred_emotion.softmax(dim=1)
            e_loss = self.emotion_loss_fn(pred_emotion, y_emotion.float())
            v_loss = self.valence_loss_fn(pred_valence, y_valence)
            a_loss = self.arousal_loss_fn(pred_arousal, y_arousal)
            loss = e_loss + v_loss + a_loss
            results["loss"] = loss
            results["e_loss"] = e_loss
            results["e_acc"] = self._e_acc_fn(
                pred_emotion.sigmoid(), y_emotion)
            results["v_loss"] = v_loss
            results["a_loss"] = a_loss

        return results

    def training_step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]] = None, batch_idx: Optional[int] = None,
        optimizer_idx: Optional[int] = None, hiddens: Optional[Tensor] = None
    ) -> Dict[str, Tensor]:
        return self.step(batch)

    def validation_step(self, batch: Optional[Union[Tensor, Sequence[Tensor]]] = None, batch_idx: Optional[int] = None,
        dataloader_idx: Optional[int] = None
    ) -> Dict[str, Tensor]:
        return self.step(batch)

    def configure_optimizers(self):
        optimizer = Adam(self.parameters(), lr=self.learning_rate, betas=(0.5, 0.9))
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": ReduceLROnPlateau(optimizer, factor=0.5, patience=10, verbose=True, min_lr=1e-8),
                "monitor": "val_loss"
            }
        }

    @staticmethod
    def _s_acc_fn(pred_s, y_s):
        s_acc = (torch.argmax(pred_s, dim=1) == y_s).float().mean()
        return s_acc

    @staticmethod
    def _e_acc_fn(pred_e, y_e):
        e_acc = ((pred_e > 0.5) == y_e).float().mean()
        return e_acc


_roberta_zh: Optional[BertModel] = None
_tokenizer_zh: Optional[BertTokenizer] = None


def get_roberta_zh() -> BertModel:
    global _roberta_zh
    if _roberta_zh is None:
        _roberta_zh = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext-large")
    return _roberta_zh


def get_tokenizer_zh() -> BertTokenizer:
    global _tokenizer_zh
    if _tokenizer_zh is None:
        _tokenizer_zh = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext-large")
    return _tokenizer_zh


_linguistic_model_zh = None


def get_linguistic_model_zh() -> LinguisticHeadZh:
    global _linguistic_model_zh
    if _linguistic_model_zh is None:
        _linguistic_model_zh = LinguisticHeadZh(finetune=False).load_from_checkpoint(LINGUISTIC_MODEL_ZH_PATH,
            strict=False, map_location=DEVICE)
        _linguistic_model_zh = _linguistic_model_zh.to(DEVICE)

    return _linguistic_model_zh
