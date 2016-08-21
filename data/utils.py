#!/usr/bin/env python2.7

ENGLISH_STOPWORDS = {
    "a", "an", "the",
    "be", "is", "been",
    "being", "was", "were",
    "are", "has", "have",
    "had",
    "here", "there", "do",
    "how", "i", "i'd",
    "i'll", "i'm", "i've",
    "me", "my", "myself",
    "can", "could", "did",
    "do", "does", "doing",
    "must", "should", "would",
     "you", "you'd", "you'll",
    "you're", "you've", "your",
    "yours", "yourself", "yourselves",
     "he", "he'd", "he'll",
    "he's", "her", "here",
    "here's", "hers", "herself",
    "him", "himself", "his",
    "she", "she'd", "she'll",
    "she's", "it", "it's",
    "its", "itself", "we",
    "we'd", "we'll", "we're",
    "we've", "their", "theirs",
    "them", "themselves", "then",
    "there", "there's", "they",
    "they'd", "they'll", "they're",
    "they've", "let", "let's",
    "this", "that", "these",
    "those", "what", "what's",
    "which", "how", "how's"
}

word2num = {'one':   1, 'eleven':     11,
            'two':   2, 'twelve':     12,
            'three': 3, 'thirteen':   13,
            'four':  4, 'fourteen':   14,
            'five':  5, 'fifteen':    15,
            'six':   6, 'sixteen':    16,
            'seven': 7, 'seventeen':  17,
            'eight': 8, 'eighteen':   18,
            'nine':  9, 'nineteen':   19,
            'ten':     10,
            'twenty':  20,
            'thirty':  30,
            'forty':   40,
            'fifty':   50,
            'sixty':   60,
            'seventy': 70,
            'eighty':  80,
            'ninety':  90
}

def is_stopword(w):
    return w in ENGLISH_STOPWORDS
