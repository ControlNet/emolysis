from typing import Dict, Tuple, Optional, Union, Sequence

import torch
from tensorneko import NekoModel
from tensorneko.layer import Linear
from torch import Tensor
from torch.nn import ReLU, CrossEntropyLoss, BCEWithLogitsLoss, MSELoss
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from transformers import BertModel, BertTokenizer

from util.consts import LINGUISTIC_MODEL_PATH, DEVICE


class LinguisticHead(NekoModel):

    def __init__(self, learning_rate: float = 1e-5, finetune: bool = False):
        super().__init__("linguistic_head")
        self.roberta = get_roberta()
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


_roberta: Optional[BertModel] = None
_tokenizer: Optional[BertTokenizer] = None


def get_roberta() -> BertModel:
    global _roberta
    if _roberta is None:
        _roberta = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext-large")
    return _roberta


def get_tokenizer() -> BertTokenizer:
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext-large")
    return _tokenizer


_linguistic_model = None


def get_linguistic_model():
    global _linguistic_model
    if _linguistic_model is None:
        _linguistic_model = LinguisticHead(finetune=False).load_from_checkpoint(LINGUISTIC_MODEL_PATH,
            strict=False, map_location=DEVICE)
        _linguistic_model = _linguistic_model.to(DEVICE)

    return _linguistic_model
