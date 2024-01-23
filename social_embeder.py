from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from discord import Embed
import re
import requests
from urllib import parse

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

def find_url(message):
  url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message)
  return url 


def check_social(message):
    for insta in ["https://instagram.com/", "https://www.instagram.com/"]:
        if insta in message:
            return (True, "Instagram")
    for twitter in ["https://twitter.com/", "https://x.com/", "https://www.twitter.com/", "https://www.x.com/"]:
        if twitter in message:
            return (True, "Twitter")
    for reddit in ["https://reddit.com/", "https://www.reddit.com/"]:
        if reddit in message:
            return (True, "Reddit")
    return (False, None)

def embed_reel(url):
    reel_url = url.replace('instagram.com', 'ddinstagram.com')
    return reel_url


def embed_instagram(message):
    if "https://instagram.com" in message: return message.replace("https://instagram.com", "https://ddinstagram.com")
    elif "https://www.instagram.com" in message: return message.replace("https://www.instagram.com", "https://ddinstagram.com")

def embed_twitter(message):
    if "https://x.com/" in message: return message.replace("https://x.com/", "https://fxtwitter.com/")
    elif "https://www.x.com/" in message: return message.replace("https://www.x.com/", "https://fxtwitter.com/")
    elif "https://twitter.com/" in message: return message.replace("https://twitter.com/", "https://fxtwitter.com/")
    elif "https://www.twitter.com/" in message: return message.replace("https://www.twitter.com/", "https://fxtwitter.com/")

def embed_reddit(message):
    if "https://reddit.com" in message: return message.replace("https://reddit.com", "https://www.rxddit.com")
    elif "https://www.reddit.com" in message: return message.replace("https://www.reddit.com", "https://www.rxddit.com")