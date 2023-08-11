from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv


class HTML:
    SHOW_MORE_BUTTON = "//div[@class='show-more']"
    TWEETS = ".tweet-content"

def webdriver_options() -> Options:
    options = Options()
    options.add_argument("--headless")
    
    return options

def start_webdriver(url: str) -> webdriver:
    driver = webdriver.Firefox(options=webdriver_options())
    print("=== webdriver init ===")
    driver.get(url)
    print("=== redirect to tweets profile ===")
    return driver

def scrape_tweets(driver: webdriver, limit: int = 100, page: int = 1) -> csv:
    TWEET_CORPUS = []

    try:
        while True:
            # Try to find the "show more" button and click it
            load_more_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, HTML.SHOW_MORE_BUTTON)))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tweets = soup.select(HTML.TWEETS)
            for tweet in tweets:
                TWEET_CORPUS.append(tweet.get_text())
                
            # click show more / next page
            load_more_button.click()
            print(f"Scrape Page: {page}")

            page += 1        
            
            if len(TWEET_CORPUS) >= limit:
                print("=== done! ===")
                
                print(f"success scrapping {len(TWEET_CORPUS)} tweets")
                break
            
    except Exception as e:
        print("Finished loading all content or an error occurred:", str(e))
        
    df = pd.DataFrame(TWEET_CORPUS, columns=['tweets'])
    
    return df
              