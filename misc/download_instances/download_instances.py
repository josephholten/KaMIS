import urllib.request
from bs4 import BeautifulSoup
import requests
import shutil

url = 'https://www.cc.gatech.edu/dimacs10/archive/clustering.shtml'
r = requests.get(url)
soup = BeautifulSoup(r.text, features="html5lib")

skip_first_n = 0
downloaded = 0

for a_tag in soup.find_all('a'):
    link = a_tag.get("href")
    link = (url[:url.rfind('/')+1] if link[:2] != "ht" else "") + link  # some links are local, need full link
    if link.find("data/clustering") != -1:   # correct type of link
        if downloaded < skip_first_n:
            downloaded += 1
        else:
            print(link)
            download_location = "instances/" + link[link.rfind('/')+1:]
            with urllib.request.urlopen(link) as response, open(download_location, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)