from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=
        [logging.FileHandler('app.log'),
        logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

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
        logger.info('Prediction successful')
        return {'length' : len(input.comments)}
    except Exception as e:
        logger.exception('Prediction failed: %s',e)
        raise HTTPException(status_code=500, detail='Prediction error')
