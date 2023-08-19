from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from nitterharvest.profileScrapper import profile_tweets
from nitterharvest.searchScrapper import search_tweets
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("./indonesian-roberta-base-sentiment-classifier/")
model = AutoModelForSequenceClassification.from_pretrained("./indonesian-roberta-base-sentiment-classifier/")

nlp = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer
)

app = FastAPI()

@app.get("/")
async def welcome_page():
    return {
        "message": "Selamat datang di Tweetoxicity API homepage"
    }


class Query(BaseModel):
    txt: Union[str, None] = None
    
@app.post("/scrapper/profile")
async def nitter_selenium_scrapper_profile(username: Query):
    
    tweets = profile_tweets(username=username.txt, limit=100)
    
    return {
        "data": tweets 
    }

@app.post("/scrapper/search")
async def nitter_selenium_scrapper_search(query: Query):
    
    tweets = search_tweets(query=query.txt, limit=100)
    
    return {
        "data": tweets
    }

    
class Tweets(BaseModel):
    tweets: Union[list, None] = None

@app.post("/preprocessing")
async def preprocessing(tweets: Tweets):
    import re, string
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
    from nltk import word_tokenize
    import pandas as pd
    import nltk
    nltk.download('punkt')

    def bersih_text(text): # first
        text = str(text)
        text = text.lower()
        text = re.sub("@[A-Za-z0-9_]+", "", text)  # Menghapus @<name> [mention twitter]
        text = re.sub("#\w+", "", text)
        text = re.sub("\[.*?\]", "", text)
        text = re.sub("https?://\S+|www\.\S+", "", text)
        text = re.sub("<.*?>+", "", text)
        text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
        # text = re.sub('\n', '', text)
        text = re.sub("\w*\d\w*", "", text)
        text = re.sub("\d+", "", text)
        text = re.sub("\s+", " ", text).strip()
        # text = re.sub('\n', '', text) jadi:
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        return text

    def tokennization(text): # second
        return word_tokenize(text)

    def stopword(text): # third
        return [word for word in text if word not in StopWordRemoverFactory().get_stop_words()]
    
    
    
    data = tweets.tweets
    df = pd.DataFrame.from_records(data).fillna(0)
    df['tweets_clean'] = df['tweet'].apply(lambda x: bersih_text(x)).apply(tokennization).apply(stopword).apply(lambda x: " ".join(x))
    df = df[df['tweets_clean'].apply(lambda x: len(x.split())) >= 1]
    
    return {
        "data": df.to_dict(orient="records")
    }
    
    
@app.post("/prediction")
async def predict_sentiment(tweets: Tweets):

    try:
        data = tweets.tweets

        data_clean = [tweet['tweets_clean'] for tweet in data]
        sentiment = [nlp(tweet)[0] for tweet in data_clean]
        final_data = [{**dict1, **dict2} for dict1, dict2 in zip(data, sentiment)]

    except Exception as error:
        print(error)  

    return {
        "data": final_data
    }
