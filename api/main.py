from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import logging
import torch


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=
        [logging.FileHandler('app.log'),
        logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

model = XLMRobertaForSequenceClassification.from_pretrained('./model')
tokenizer = XLMRobertaTokenizer.from_pretrained('./model')

vader = SentimentIntensityAnalyzer()

def return_sentiment(comment):
            score = vader.polarity_scores(comment)['compound']
            label = None
            if score >= 0.05:
                label = 'Positive'
            elif score <= -0.05:
                label = 'Negative'
            else:
                label = 'Neutral'
            return label

app = FastAPI()

class commentsinput(BaseModel):
    comments : list[str]

@app.get('/')
def home():
    return {'message' : 'Server is running!'}

@app.post('/predict')
def predict(input: commentsinput):
    if not input.comments:
        logger.error('Comment field empty')
        raise HTTPException(status_code=400, detail='Comments field empty')
    
    logger.info("Comment batch of %s comments recieved",len(input.comments))
    
    try:

        #roberta
        comment_tokens = tokenizer(input.comments, padding=True, truncation=True, return_tensors='pt')  
        outputs = model(**comment_tokens)  
        pred = torch.argmax(outputs.logits, dim=1)
        predictions = pred.numpy().tolist()

        label_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}

        roberta_preds = []
        for p in predictions:
            roberta_preds.append(label_map[p])

        #vader
        vader_preds = []
        for comment in input.comments:
            vader_preds.append(return_sentiment(comment))

        logger.info('Prediction successful')

        return {'xlm-ROBERTa Predictions' : roberta_preds,
                'VADER Predictions' : vader_preds}
    
    except Exception as e:
        logger.error('Prediction failed: %s',e)
        raise HTTPException(status_code=500, detail=e)
