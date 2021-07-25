# -*- coding: utf-8 -*-

import spacy
from spacy.lang.ru import Russian
from spacy.lang.ru.stop_words import STOP_WORDS
from nltk.corpus import stopwords


import re
import string

class text_preprocessing():

    def __init__(self, text):
        self.text = text
        self.text_tokens = []
        self.text_lemmas = []
        self.nltk_stop_words = stopwords.words('russian')
        self.nlp = spacy.load('ru_core_news_lg')
        self.russian_profanity_wordlist = ['бля', 'блять']
        self.english_profanity_wordlist = ['bitch', 'slut', 'whore', 'hoe']


    def clean_text(self):
        self.text = self.text.lower()
        self.text = re.sub('\[.*?\]', '', self.text)
        self.text = re.sub("\\W"," ",self.text) 
        self.text = re.sub('https?://\S+|www\.\S+', '', self.text)
        self.text = re.sub('<.*?>+', '', self.text)
        self.text = re.sub('[%s]' % re.escape(string.punctuation), '', self.text)
        self.text = re.sub('\n', '', self.text)
        self.text = re.sub('\w*\d\w*', '', self.text)

    def tokenize_text(self):        
        self.text_tokens = [token.text for token in self.nlp(self.text)]
    
    def lemmatize_text(self):
        self.text_lemmas = [token.lemma_ for token in self.nlp(self.text) if token.like_num == False]

    def remove_stop_words(self):
        self.text_tokens = [word for word in self.text_lemmas if word not in STOP_WORDS and word not in self.russian_profanity_wordlist]
        self.text_tokens = [word for word in self.text_tokens if word not in self.nltk_stop_words]
        self.text_tokens = [word for word in self.text_tokens if len(word) > 2 and word != len(word) * word[0]]
        self.text_tokens = [word for word in self.text_tokens if word not in [word for word in self.text_tokens if 97 <= ord(word[0]) <= 122 and word not in self.english_profanity_wordlist]]
        self.text_tokens = [word for word in self.text_tokens if word != ' '] 
        self.processed_text = ' '.join(self.text_tokens)  


def preprocess_text(text):
    obj = text_preprocessing(text)
    obj.clean_text()
    obj.tokenize_text()
    obj.lemmatize_text()
    obj.remove_stop_words()

    return obj.processed_text

