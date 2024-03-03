#!/usr/bin/python3
import json
import os
import re
import string
import shutil

import pandas as pd

import pickle as pk

from bertopic import BERTopic

import nltk
from nltk.corpus import stopwords
#nltk.download("stopwords")
from nltk.tokenize import word_tokenize
#nltk.download("punkt")

##################################################
#KEYWORDS

keywords = [ ["security"],
             ["defence"],
             ["safety"],
             ["collateral"],
             ["privacy"],
             ["confidentiality"],
             ["isolation"],
             ["confidence"],
             ["privateness"],
             ["segregation"],
             ["malicious"],
             #["malevolent"],
             #["evil"],
             #["good"],
             #["sinister"],
             #["benevolent"],
             #["humane"],
             ["vulnerability"],
             ["accountability"],
             ["authenticity"],
             ["susceptibleness"],
             ["attack"],
             ["intrusion"],
             ["interference"],
             ["hacking"],
             ["disable"],
             ["hacker"],
             #["programmer"],
             ["attacker"],
             ["assailant"],
             ["exploit"],
             ["tamper"],
             ["exploitation"],
             ["exploited"],
             ["exploiting"],
             ["vulnerable"],
             ["susceptible"],
             ["vulnerabilities"],
             #["society"],
             #["civilization"],
             #["development"],
             #["improvement"],
             #["economy"],
             #["chatgpt"],
             ["algorithms"],
             #["bussinesses"],
             #["prospects"],
             ["intelligence"],
             #["openai"],
             ["generate"],
             ["automation"],
             ["secured"],
             ["hackers"],
             ["securities"],
             ["intelligent"],
             ["artificial"],
             ["authorization"],
             ["authentication"],
             ["dangers"],
             ["hack"] ]

##################################################
#HELPER FUNCS

def load_raw_docs():
    with open("raw_docs.json", "r") as f:
        return json.load(f)


def save_filtered_docs(data):
    with open("filtered_docs.json", "w") as outfile:
        json.dump(data, outfile)

def load_filtered_docs():
    with open("filtered_docs.json", "r") as f:
        return json.load(f)

#Same as save_filtered_docs except strings saved unclean
def save_selected_docs(data):
    with open("selected.json", "w") as outfile:
        json.dump(data, outfile)

#Same as load_filtered_docs except strings saved unclean
def load_selected_docs():
    with open("selected.json", "r") as f:
        return json.load(f)


def pickelize(obj,file_path):
    with open(file_path,"wb") as f:
        pk.dump(obj,f)

def un_pickelize(file_path):
    with open(file_path,"rb") as f:
        return(pk.load(f))

##################################################
#FILTER

def remove_urls(text):
    return re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', ' ', text, flags=re.MULTILINE)

def remove_multispace(text):
    return " ".join(text.split())

def preprocess_text(text):
    # Remove punctuation
    text = re.sub(f"[{string.punctuation}]", " ", text) #!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    words = word_tokenize(text)
    words = [word for word in words if word not in set(stopwords.words("english"))]
    return " ".join(words)

def remove_whitespace_chars(text):
    return re.sub(r"[\n\t\r]*", "", text)

def filter_docs():
    print("Filtering docs")
    data = load_raw_docs()
    filtered = []
    selected = []

    idx = 0
    for i in data:
        idx += 1
        print(idx)
        select = i
        #Clean data
        s = i
        s = s.lower()
        s = remove_urls(s)
        s = remove_multispace(s)
        s = preprocess_text(s)

        #Keyword search data
        if "gpt" in s:
            for kw_lst in keywords:
                if all((kw in s for kw in kw_lst)):
                    selected.append(select)
                    filtered.append(s)
                    break


    print("filtered out {} docs".format(len(filtered)))
    save_filtered_docs(filtered)
    save_selected_docs(selected)


##################################################
### MAIN TRAINING FUNCTION ###

def train_model():
    print("Training model")
    data = load_filtered_docs()
    topic_model = BERTopic(verbose=True, calculate_probabilities=True)
    topics, probs = topic_model.fit_transform(data)
    topic_model.save("filtered_model")
    pickelize(topics,"topics")
    pickelize(probs,"probs")

##################################################
#Data extraction and parsing

#########################
#Topics strings

def get_topics_str(topic_model): #-> dict[id,topic_str]
    to_ret = {}
    for k,v in topic_model.get_topics().items():
        words = [x[0] for x in v]
        topic_str = " ".join(words)
        to_ret[k] = topic_str
    return to_ret

#Write topics to disk
def write_topics_str():
    print("Wrinting topic string")
    topic_model = BERTopic.load("filtered_model")
    topics = get_topics_str(topic_model)
    with open(f"topics.txt", "w") as outfile:
        for k,v in topics.items():
            outfile.write("{:2}, {}\n".format(k,v))

#########################
#Topics docs

def clean_topics_docs():
    folder = '/home/gusbo010/reddit-scraper/src/outp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def write_topics_docs_to_os(topics_docs, topics):
    for k,v in topics_docs.items():
        f_name = "{}_{}_{}".format(k, topics[k][0], topics[k][1][:150])
        path = os.path.join("/home/gusbo010/reddit-scraper/src/outp", f_name)
        with open(f"{path}.txt", "w") as outfile:
            for i in v:
                doc = remove_whitespace_chars(i[1])
                outfile.write(f"{i[0]} -- {doc}\n")


#Get a dict of topics {id:(count,name)}
def get_topic_dict(topic_model):
    to_ret = {}
    for i in topic_model.get_topic_info().iterrows():
        t = tuple(i[1])
        to_ret[t[0]] = (t[1], t[2])
    return to_ret


#write one file per most relevant topic
def write_topics_docs():
    print("Wrinting topic docs")
    docs = load_filtered_docs()
    selected = load_selected_docs()
    topic_model = BERTopic.load("filtered_model")
    topics = get_topic_dict(topic_model)
    topics_docs = {}
    document_info = topic_model.get_document_info(docs)
    itter = document_info.iterrows()
    for idx in range(len(document_info)):
        i = next(itter)
        t = tuple(i[1]) #Document:str, Topic:int, Name, Top_n_words, Probability, Representative_document
        if t[1] in topics_docs:
            topics_docs[t[1]].append( ( t[4], selected[idx] ) )
        else:
            topics_docs[t[1]] = [ ( t[4], selected[idx] )  ]
    clean_topics_docs()
    write_topics_docs_to_os(topics_docs, topics)


def calc_prob():
    #topics = un_pickelize("topics")
    probs = un_pickelize("probs")
    probs_df=pd.DataFrame(probs)

    sums = pd.DataFrame({'sum': probs_df.sum(axis=0)})
    all_sum = pd.DataFrame({'all_sum': sums.sum(axis=0)})
    all_sum = float(all_sum.iat[0,0])

    sums['prevalance'] = sums.apply(lambda row : pd.Series(row["sum"]/all_sum), axis=1)

    topic_model = BERTopic.load("filtered_model")
    topics = get_topic_dict(topic_model)
    sums["topic"] = pd.Series([x[1] for x in topics.values()])

    with open(f"probability.txt", "w") as outfile:
        outfile.write(sums.to_string()+"\n")
        outfile.write(f"All sum: {all_sum}\n")


##################################################
#Data extraction and parsing
def visualize_barchart():
    print("visualize_barchart")
    topic_model = BERTopic.load("filtered_model")
    fig = topic_model.visualize_barchart(top_n_topics=12)
    fig.write_image("barchart.svg")


def visualize_topics():
    print("visualize_topics")
    topic_model = BERTopic.load("filtered_model")
    fig = topic_model.visualize_topics()
    fig.write_image("visual.svg")


def visualize_distribution():
    print("visualize_distribution")
    topic_model = BERTopic.load("filtered_model")
    probs = un_pickelize("probs")
    for i in range(len(probs)):
        path = os.path.join("/home/gusbo010/reddit-scraper/src/distribu", f"{i}_distribution.svg")
        fig = topic_model.visualize_distribution(probs[i], min_probability=0.000001)
        fig.write_image(path)

def visualize_hierarchy():
    print("visualize_hierarchy")
    topic_model = BERTopic.load("filtered_model")
    probs = un_pickelize("probs")
    fig = topic_model.visualize_hierarchy()
    fig.write_image("hierarchy.svg")



if __name__ == "__main__":
    #filter_docs()
    #train_model()
    #write_topics_str()
    #write_topics_docs()
    #calc_prob()
    #visualize_barchart()
    #visualize_topics()
    #visualize_hierarchy()
    visualize_distribution()
