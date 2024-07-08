# ----- DEPENDENCY -----
import streamlit as st
import streamlit_ext as ste
import requests
import json
import pandas as pd
from streamlit_echarts import st_echarts
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from collections import Counter
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

# ----- PAGE SETTING -----
PAGE_TITLE = "Tweetoxicity"
PAGE_ICON = Image.open("icon/rsz_1tweetox.png")

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# CSS Styling
css = '''
<style>
    section.main > div {max-width:65rem}
    @media screen and (min-width: 601px) {
        h1 {
            font-size: 80px;
            text-align: center;
        }

    @media screen dan (max-width: 600px) {
        h1 {
            font-size: 40px;
            text-align: center;
        }
    }

    h1 {
        text-align: center;
    }

    .description {
        text-align: center;
        font-size: 20px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# ----- FRONT END -----
st.markdown("<h1 style='text-align: center;'>Tweetoxicity</h1><br/>", unsafe_allow_html=True)
st.markdown("<p class='description' style='text-align: center;'>Tweetoxicity adalah aplikasi web yang menganalisis perilaku pengguna Twitter/X di Indonesia berdasarkan aktivitas profil X mereka. Program ini menggunakan klasifikasi sentimen untuk memberikan penilaian sentimen bagi pengguna berdasarkan tweet atau retweet terbaru mereka.</p><br /><br />", unsafe_allow_html=True)

# ----- BACKEND -----
## --- CONFIG ---
class CONFIG:
    url = os.getenv("API_URL")

## --- API Calls ---
@st.cache_data(show_spinner=False)
def api_post(endpoint: str, data: dict):
    response = requests.post(CONFIG.url + endpoint, json=data)
    response.raise_for_status()  # Akan memunculkan HTTPError untuk respons yang buruk
    return response.json()

def scrapper_profile(username: str):
    return api_post("/scrapper/profile", {"txt": username})

def scrapper_search(query: str):
    return api_post("/scrapper/search", {"txt": query})

def prediction(tweets: list):
    return api_post("/prediction", {"tweets": tweets})

## --- Utility Functions ---
def display_sentiment_result(username: str, calc_sentiment: pd.DataFrame):
    get_most_sentiment = calc_sentiment.sort_values(by="tweet", ascending=False).iloc[0]
    sentiment_messages = {
        "negative": f"{username.title()} perlu istirahat dari X. Sebagian besar tweet terbaru {username.title()} memiliki sentimen negatif.",
        "positive": f"{username.title()} cukup keren. Sebagian besar tweet terbaru {username.title()} memiliki sentimen positif.",
        "neutral": f"{username.title()} cukup santai. Sebagian besar tweet terbaru {username.title()} memiliki sentimen netral."
    }
    sentiment_colors = {
        "negative": "#dc143c",
        "positive": "#2e8b57",
        "neutral": "#f1b04c"
    }
    st.markdown(f"<p style='text-align: center; color: {sentiment_colors[get_most_sentiment['label']]};'>{sentiment_messages[get_most_sentiment['label']]}</p><br />", unsafe_allow_html=True)

def create_pie_chart(calc_sentiment: pd.DataFrame):
    sentiment_colors = {
        "negative": "#dc143c",
        "positive": "#2e8b57",
        "neutral": "#f1b04c"
    }
    
    data_count = [
        {"value": count, "name": title.title(), "itemStyle": {"color": sentiment_colors[title]}}
        for title, count in zip(calc_sentiment['label'], calc_sentiment['tweet'])
    ]
    
    options = {
        "tooltip": {"trigger": "item"},
        "series": [
            {
                "name": "Sentimen",
                "type": "pie",
                "radius": "75%",
                "data": data_count,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }
        ]
    }
    return options

# Initialize the stopword remover
stopword_factory = StopWordRemoverFactory()
stop_words = set(stopword_factory.get_stop_words())
def create_wordcloud(text_wordcloud: list, query: str):
    # Ganti query dengan string kosong di setiap tweet
    text_wordcloud = [tweet.lower().replace(query, '') for tweet in text_wordcloud]
    
    # Remove stopwords
    text_wordcloud = [" ".join([word for word in tweet.split() if word not in stop_words]) for tweet in text_wordcloud]

    # Buat data word cloud
    cont = Counter(" ".join(text_wordcloud).split())
    cont_most_common = cont.most_common(30)
    data = [{"name": name, "value": value} for name, value in cont_most_common]
    wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
    return wordcloud_option

@st.cache_data(show_spinner=False)
def convert_df_to_csv(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def process_data(scrap_data: dict, query: str):
    if not scrap_data['data']:
        st.error(f"Maaf, kami tidak dapat mengunduh tweet karena profil bersifat pribadi atau tidak ada.", icon="🚨")
        return None

    with st.spinner("Memprediksi Sentimen..."):
        predictions = prediction(scrap_data['data'])

    df = pd.DataFrame.from_records(predictions['data']).fillna(0)
    calc_sentiment = df.groupby("label")['tweet'].count().reset_index()
    
    display_sentiment_result(query, calc_sentiment)

    pie_chart_options = create_pie_chart(calc_sentiment)
    wordcloud_option = create_wordcloud(df['tweet'].values, query)

    col1, col2 = st.columns(2)
    with col1:
        st_echarts(wordcloud_option)
    with col2:
        st_echarts(pie_chart_options, height="300px")

    return df

def download_csv_button(df: pd.DataFrame, filename: str):
    csv_data = convert_df_to_csv(df)
    ste.download_button(
        label="Unduh data sebagai CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )

## --- STREAMLIT LOGIC ---
query = st.radio("Pilih apa yang ingin dicari...", ("Profile", "Search on X"))

if query == "Profile":
    username = st.text_input('Masukkan Username X. Contoh: "jokowi"', "")
    if username:
        try:
            with st.spinner(f"Scrapping {username}'s tweets..."):
                scrap_data = scrapper_profile(username)
            
            df = process_data(scrap_data, username)
            if df is not None:
                df = df[['time', 'tweet', 'label', 'score']]
                df['score'] = df['score'].apply(lambda x: f"{round(x*100, 2)}%")
                st.dataframe(df, use_container_width=True)
                download_csv_button(df, f"{username}_data.csv")
        except Exception as error:
            st.error(f"Terjadi kesalahan: {error}", icon="🚨")
elif query == "Search on X":
    search_query = st.text_input('Masukkan Pencarian X. Contoh: "indonesia"', "")
    if search_query:
        try:
            with st.spinner(f"Scrapping {search_query}'s tweets..."):
                scrap_data = scrapper_search(f"{search_query} lang:id")

            df = process_data(scrap_data, search_query)
            if df is not None:
                df = df[['time', 'tweet', 'username', 'label', 'score']]
                df['score'] = df['score'].apply(lambda x: f"{round(x*100, 2)}%")
                st.dataframe(df, use_container_width=True)
                download_csv_button(df, f"{'_'.join(search_query.split())}_data.csv")
        except Exception as error:
            st.error(f"Terjadi kesalahan: {error}", icon="🚨")
