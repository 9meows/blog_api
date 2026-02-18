import numpy as np
import pickle
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from app.schemas import SentimentRequest, SentimentResponse

router = APIRouter(prefix="/api", tags=["sentiment"])

# Загружает модельку
try:
    model = load_model('model/sentiment_model.keras')
    with open('model/tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    max_text_len = 100
except Exception as e:
    print(f"Ошибка загрузки модели - {e}")
    model = None
    tokenizer = None


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Ручка для анализа отзыва на позитивный/негативный
    Возвращает positive/negative и % уверенности модели
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Модель не загружена")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Текст не может быть пустым")
    
    seq = tokenizer.texts_to_sequences([request.text.lower()])
    pad = pad_sequences(seq, maxlen=max_text_len)
    
    prediction = float(model.predict(pad, verbose=0)[0][0])
    
    sentiment = "positive" if prediction >= 0.5 else "negative"
    confidence = prediction if prediction >= 0.5 else 1 - prediction
    
    return SentimentResponse(
        sentiment=sentiment,
        confidence=round(confidence, 2)
    )