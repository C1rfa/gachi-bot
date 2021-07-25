import requests as req
from bs4 import BeautifulSoup as bs
import codecs

page = codecs.open('./gachi.html', 'r', "utf_8_sig").read()
text = bs(page, features="html5lib")
mydivs = text.find_all("div", class_="audio_row_with_cover")

file = open('./songs.txt', 'w')

for div in mydivs:
    file.write(div['data-full-id'] +'\n')