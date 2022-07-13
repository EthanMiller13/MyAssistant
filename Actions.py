import pyjokes
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import datetime
import pywhatkit as wtk  # Youtube playing
import wikipedia  # wikipedia info
import googlesearch as gs  # google search
import smtplib  # mail
import time  # sleep func
import webbrowser as web
import os


import warnings

warnings.catch_warnings()

warnings.simplefilter("ignore")

def get_joke():
    return pyjokes.get_joke()

def googlesearch(search_key: str):
    data = []
    results = search(search_key, num_results=5)
    for url in results:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        title = str(soup.find("title"))

        metas = soup.find_all('meta')
        descriptions = [meta.attrs['content'] for meta in metas
                        if 'name' in meta.attrs and meta.attrs['name'] == 'description']
        data.append([title, url, descriptions])
    return data


def wikisearch(search_key):
    try:
        return wikipedia.summary(wikipedia.search(search_key)[0])
    except IndexError:
        return None
    except wikipedia.exceptions.PageError:
        return None


def get_date():
    today = datetime.date.today()
    date = today.strftime("%B %d, %Y")
    return date


def get_time():
    time = datetime.datetime.now().strftime('%I:%M %p')
    return time
