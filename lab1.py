import re
from stemming.porter2 import stem
file = open("quran.txt", "r")
#print(file.read())
stop_words = open("englishST.txt","r")
chop = lambda x: x[:-1]
stop_words = list(map(chop,stop_words.readlines()))
print(stop_words)

def tokenization(text):
    return list(filter(None,re.split("[^a-zA-Z]",text)))


def case_folding(text):
    return text.lower()


def stopping(words,l_o_sw):
    for i in l_o_sw:
        return list(filter(i,words))

def stem_list_of_words(l_o_w):
    return list(map(stem,l_o_w))