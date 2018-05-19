# coding: utf-8

import urllib.request
from urllib.error import HTTPError
import time
from bs4 import BeautifulSoup
import csv
import sys
import os.path

dictUrl = "https://en.oxforddictionaries.com/definition/"
youdaoUrl = "http://www.youdao.com/w/eng/"
headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
}

opener = urllib.request.build_opener()
urllib.request.install_opener(opener)

# opens a file and returns a list containing the lines
def read_input_file(filename):
    try:
        f = open(filename, 'r')
        return f.readlines()
    except IOError:
        print("Error opening or reading input file:", filename)
        sys.exit()


# breaks up the line into separate words and returns a list containing all the words
def get_words_from_line(L):
    input_list = []
    for line in L:
        words_in_line = get_words_from_string(line)
        input_list = input_list + words_in_line
    return input_list


# breaks up the line into separate words
def get_words_from_string(line):
    word_list = []
    character_list = []
    
    for c in line:
        if c.isalnum():
            character_list.append(c)
        elif len(character_list) > 0:
            word = "".join(character_list)
            word = word.lower()
            word_list.append(word)
            character_list = []
    if len(character_list) > 0:
        word = "".join(character_list)
        word = word.lower()
        word_list.append(word)
    return word_list


def write_one_word_result(dict,csvfile,file_exists):
    
    # write header
    # in order to get all the fields, first get an arbitary item from the dict
    writer = csv.DictWriter(csvfile, fieldnames = dict.keys())
    
    if not file_exists:
        writer.writeheader()

    print(dict)
    writer.writerow(dict)

def search_for_one_word(word):
    query_result = {}
    youdao_query_result = {}

    query_url = dictUrl + word
    youdao_query_url = youdaoUrl + word

    # get definition and sentence from oxforddictionaries
    # fields in query_result are definition and sentence
    query_result = get_query_result(query_url)

    # get chinese definition and phonetic from youdao
    # fields in youdao_query_result are phonetic and chinese_definition
    youdao_query_result = get_youdao_query_result(youdao_query_url)

    result = {**query_result, **youdao_query_result, "word":word}

    return result
        
# @parameter word_list is a list of word
def search_and_write_result(word_list,filename):
    csvfile = open(filename, 'a')

    # determine whether the file already exits, in order to decide whether to write header
    file_exists = os.path.isfile(filename)

    for word in word_list:
        # search results for each word is a dict
        result = search_for_one_word(word)

        # write search results to output file one by one
        write_one_word_result(result,csvfile,file_exists)
    

def get_query_result(url):
    page = urllib.request.Request(url, headers = headers)
    result = {}

    try:
        response = urllib.request.urlopen(page)
        soup = BeautifulSoup(response,'lxml')
        
        # find the first element with class 'ind', which is the definition of the word
        definition_object = soup.find(attrs={'class':'ind'})
        definition = definition_object.text if definition_object is not None else ''
        result["definition"] = definition
        
        sentence_object = soup.find(attrs={'class':'exg'})
        sentence = sentence_object.find('em').text if sentence_object is not None else ''
        result["sentence"] = sentence
        return result
    except HTTPError as e:
        print("HttpError: ", e.read())

# search for chinese definition and phonetic in youdao dictionary
def get_youdao_query_result(url):
    page = urllib.request.Request(url, headers = headers)
    result = {}
    try:
        response = urllib.request.urlopen(page)
        soup = BeautifulSoup(response,'lxml')
        
        phonetic_object = soup.find(attrs={'class':'phonetic'})
        phonetic = phonetic_object.text if phonetic_object is not None else ''
        result["phonetic"] = phonetic
        
        chinese_definition_object = soup.find(attrs={'class':'trans-container'})
        chinese_definition = chinese_definition.find('li').text if chinese_definition is not None else ''
        result["chinese_definition"] = chinese_definition
        return result
    except HTTPError as e:
        print("HttpError: ", e.read())


def main():
    if len(sys.argv) < 2:
        print("Usage: word_query_to_anki.py inputfile outputfile.csv")
    else:
        input_file_name = sys.argv[1]
        output_file_name = sys.argv[2] if len(sys.argv) == 3 else "output.csv"

        
        file_line = read_input_file(input_file_name)
        input_list = get_words_from_line(file_line)
        query_result = search_and_write_result(input_list,output_file_name)

main()