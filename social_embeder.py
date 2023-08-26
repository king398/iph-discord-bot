from selenium import webdriver, common
from selenium.webdriver.common.by import By
from discord import Embed
import re

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument("--no-sandbox") 
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-dev-shm-using")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=46577")

driver = webdriver.Chrome(options=options)

def find_url(message):
  url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message)
  return url 


def check_social(message):
    url = find_url(message)
    for insta in ["https://instagram.com/", "https://www.instagram.com/"]:
        if insta in url:
            return (True, "Instagram")
    for twitter in ["https://twitter.com/", "https://x.com/", "https://www.twitter.com/", "https://www.x.com/"]:
        if twitter in url:
            return (True, "Twitter")
    return (False, None)

def embed_reel(url):
    driver.get(url)
    reel_url = driver.find_element(by=By.TAG_NAME, value="video").get_attribute(name='src')
    title = driver.find_element(by=By.NAME, value="twitter:title").get_attribute(name='content')
    description = ''
    for el in driver.find_elements(by=By.TAG_NAME, value="meta"):
        if el.get_attribute('property') == 'og:title':
            description = el.get_attribute('content')
    embed = Embed(
        title=title,
        description=description,
        url=reel_url
    )
    return embed


def embed_instagram(message):
    if "https://instagram.com" in message: return message.replace("https://instagram.com", "https://ddinstagram.com")
    elif "https://www.instagram.com" in message: return message.replace("https://www.instagram.com", "https://ddinstagram.com")

def embed_twitter(message):
    if "https://x.com/" in message: return message.replace("https://x.com/", "https://fxtwitter.com/")
    elif "https://www.x.com/" in message: return message.replace("https://www.x.com/", "https://fxtwitter.com/")
    elif "https://twitter.com/" in message: return message.replace("https://twitter.com/", "https://fxtwitter.com/")
    elif "https://www.twitter.com/" in message: return message.replace("https://www.twitter.com/", "https://fxtwitter.com/")

