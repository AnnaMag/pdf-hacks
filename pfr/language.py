#! /usr/bin/env python
"""
Created: April, 2016, NYC
Anna M. Kedzierska
given an input text, detect the language
call: detect_language(text)
"""

from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

def get_languages(text):
    '''
    nltk.wordpunct_tokenize() splits all punctuations into separate tokens

    >>> wordpunct_tokenize("My name's Anna.End.")
    ['My', name', 's', 'Anna', '.', 'End', '.']
    '''
    languages_ratios = {}

    tokens = wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    # number of unique stopwords appearing in analyzed text as included in nltk(Africaans classified as Dutch)
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        languages_ratios[language] = len(common_elements) # language "score"

    return languages_ratios


def detect_language(text):
    """
    Calculate probability of given text to be written in a given language,
    returning the highest score and ratios
    """

    ratios = get_languages(text)

    most_rated_language = max(ratios, key=ratios.get)

    return most_rated_language, ratios
