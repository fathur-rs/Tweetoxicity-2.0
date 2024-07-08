from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from nitterharvest.profileScrapper import profile_tweets
from nitterharvest.searchScrapper import search_tweets
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from tqdm import tqdm

# Initialize FastAPI app
app = FastAPI()

# Load model and tokenizer only once
tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("./indonesia-distilledbert-sentiment-classification/")

# Create sentiment analysis pipeline
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, max_length=512, truncation=True)

class Query(BaseModel):
    txt: str

class Tweets(BaseModel):
    tweets: List[dict]

@app.get("/")
async def welcome_page():
    return {"message": "Selamat datang di Tweetoxicity API homepage"}

@app.post("/scrapper/profile")
async def nitter_selenium_scrapper_profile(username: Query):
    tweets = profile_tweets(username=username.txt, limit=100)
    return {"data": tweets}

@app.post("/scrapper/search")
async def nitter_selenium_scrapper_search(query: Query):
    tweets = search_tweets(query=query.txt, limit=150)
    return {"data": tweets}

@app.post("/prediction")
async def predict_sentiment(tweets: Tweets):
    label2id = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
    data_clean = [tweet['tweet'] for tweet in tweets.tweets]  # Use raw tweet text
    
    # Batch prediction
    sentiments = nlp(data_clean, batch_size=32)
    
    converted_sentiments = [{'label': label2id[result['label']], 'score': result['score']} for result in sentiments]
    final_data = [{**tweet, **sentiment} for tweet, sentiment in zip(tweets.tweets, converted_sentiments)]
    
    return {"data": final_data}
