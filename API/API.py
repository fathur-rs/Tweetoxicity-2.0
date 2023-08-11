from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from scrapper.NitterSelenium import start_webdriver, scrape_tweets 
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


class Username(BaseModel):
    username: Union[str, None] = None
    
@app.post("/scrapper")
async def nitter_selenium_scrapper(username: Username):
    
    driver = start_webdriver(url=f'https://nitter.net/{username.username}')
    tweets = scrape_tweets(driver=driver)
    
    # convert to csv
    # tweets.to_csv(f'./csv/{username.username}.csv', index=False)
    tweets_json = tweets['tweets'].tolist()
        
    driver.quit()
    
    return {
        "data": tweets_json 
    }
    
class Tweets(BaseModel):
    tweets: Union[list, None] = None

@app.post("/preprocessing")
async def preprocessing(tweets: Tweets):
    import re, string
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
    from nltk import word_tokenize
    import nltk
    nltk.download('punkt')
    import pandas as pd

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
    df = pd.DataFrame(data, columns=['tweets'])
    df['tweets_clean'] = df['tweets'].apply(lambda x: bersih_text(x)).apply(tokennization).apply(stopword).apply(lambda x: " ".join(x))
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
