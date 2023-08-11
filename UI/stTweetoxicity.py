# ----- DEPENDENCY -----
import streamlit as st
import streamlit_ext as ste
import requests
import json
import pandas as pd
from streamlit_echarts import st_echarts
from collections import Counter
from PIL import Image

# ----- PAGE SETTING -----
PAGE_TITLE = "Tweetoxicity"
PAGE_ICON = Image.open("icon/rsz_1tweetox.png")

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

css='''
<style>
    section.main > div {max-width:65rem}
    @media screen and (min-width: 601px) {
        h1 {
            font-size: 80px;
            text-align: center;
        }

    @media screen and (max-width: 600px) {
        h1 {
            font-size: 40px;
            text-align: center;

        }
    }
    
    h1{
        text-align: center;
    }
    
    .description{
        text-align: center;
        font-size: 20px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)


# ----- FRONT END -----
st.markdown(f"<h1 style='text-align: center;'>Tweetoxicity™</h1><br/>", unsafe_allow_html=True)
st.markdown(f"<p class='description' style='text-align: center;'>TweeToxicity is a program that analyses twitter user behavior through their actions on their Twitter Profile. The program utilize machine learning to give Twitter users appropriate score according to their latest tweets or retweets. This program is meant for educational purposes and no ill intetions exists prior to creating this program.</p><br /><br />", unsafe_allow_html=True)
username = st.text_input('Input Twitter Username. e.g. "jokowi"', "")

# ----- BACKEND -----
## --- CONFIG ---
class CONFIG:
    url = "https://tweetoxicity-api-snqvw2zpga-et.a.run.app/"

## --- API ---
def scrapper(username: str):
    
    data = {
        "username": username
    }
    
    r = requests.post(CONFIG.url + "/scrapper", json=data)
    return json.loads(r.text)

def preprocessing(tweet: list):
    js = {
        "tweets": tweet
    }
    r = requests.post(CONFIG.url + "/preprocessing", json=js)
    return json.loads(r.text)

def prediction(tweet: list):
    js = {
        "tweets": tweet
    }
    r = requests.post(CONFIG.url + "/prediction", json=js)
    return json.loads(r.text)

## --- STREAMLIT LOGIC ---
if username == "":
    pass
else:
    try:
        # SCRAPPER
        with st.spinner("Scrape User Tweets..."):
            scrap_data = scrapper(username)
            
        # check if twttiet account is exist or private
        if not scrap_data['data']:
            st.error(f"Sorry we can't scrape the tweets, because {username} profile is private or does not exist....", icon="🚨")

        
        # PREPROCESSING 
        with st.spinner("Preprocessing..."):
            preprocess = preprocessing(scrap_data['data'])
    
        # PREDICTION
        with st.spinner("Predict Sentiment..."):
            predictions = prediction(preprocess['data'])   
        
        df = pd.DataFrame.from_records(predictions['data']).fillna(0)

            
        # DECIDING ACCOUNT SENTIMENT
        calc_sentiment = df.groupby("label")['tweets'].count().reset_index()
        get_most_sentiment = calc_sentiment.sort_values(by="tweets", ascending=False).reset_index(drop=True).iloc[0, :]

        if get_most_sentiment['label'] == "negative":
            st.markdown(f"<p style='text-align: center; color: #dc143c;'>{username.title()} needs a day off of Twitter. Most {username.title()} latest tweets have a negative sentiment</p><br />", unsafe_allow_html=True)
        elif get_most_sentiment['label'] == "positive":
            st.markdown(f"<p style='text-align: center; color: #2e8b57;'>{username.title()} is pretty cool. Most {username.title()} latest tweets have a positive sentiment</p><br />", unsafe_allow_html=True)
        elif get_most_sentiment['label'] == "neutral":
            st.markdown(f"<p style='text-align: center; color: violet;'>{username.title()} is pretty chill. Most {username.title()} latest tweets have a neutral sentiment</p><br />", unsafe_allow_html=True)
            
    #     # PIE CHART
        data_count = []
        for title, count in zip(calc_sentiment['label'], calc_sentiment['tweets']):
            a = {
                "value": count,
                "name": title.title()
            }
            data_count.append(a)
            
        options = {
        "tooltip": {"trigger": "item"},
        "series": [
                {
                    "name": "Sentiment",
                    "type": "pie",
                    "radius": "75%",
                    "data": data_count,
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                        }
                    },
                }
            ],
        }
        
        # WORDCLOUD
        text_wordcloud = df['tweets_clean'].values
        cont = Counter(" ".join(text_wordcloud).split())
        cont_most_common = cont.most_common(30)
        data = [
            {"name": name, "value": value}
            for name, value in cont_most_common
        ]
        wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
        
        col1, col2 = st.columns(2)
        with col1:
            st_echarts(wordcloud_option)
        with col2:
            st_echarts(options=options, height="300px")
        
        # DOWNLOAD CSV
        @st.cache_data
        def convert_df(df):
            return df.to_csv().encode('utf-8')
        
        df = df[['tweets', 'label', 'score']]
        df['score'] = df['score'].apply(lambda x: f"{round(x*100, 2)}%")
        st.dataframe(df, use_container_width=True)
        
        ste.download_button(
            label="Download data as CSV",
            data=convert_df(df),
            file_name= f"{username}_data.csv",
            mime="text/csv"
        )
        
    except IndexError:
        st.error(f"Sorry we can't scrape the tweets, because {username} profile is private....", icon="🚨")
    except Exception as error:
        print(error)
