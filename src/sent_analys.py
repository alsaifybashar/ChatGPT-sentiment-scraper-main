#!/usr/bin/python3
import json

from bertopic import BERTopic

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

import pickle as pk

################################################## WHAT DATA ?
# Load data
#Get a dict of topics {id:(count,name)}
def get_topic_dict(topic_model):
    to_ret = {}
    for i in topic_model.get_topic_info().iterrows():
        t = tuple(i[1])
        to_ret[t[0]] = (t[1], t[2])
    return to_ret

def load_topics():
    topic_model = BERTopic.load("filtered_model")
    return get_topic_dict(topic_model)

def pickelize(obj,file_path):
    with open(file_path,"wb") as f:
        pk.dump(obj,f)

def un_pickelize(file_path):
    with open(file_path,"rb") as f:
        return(pk.load(f))

#Same as load_filtered_docs except strings saved unclean
def load_filtered_docs():
    to_ret = []
    with open("filtered_docs.json", "r") as f:
        docs = json.load(f)
        for i in range(len(docs)):
            if i == 1759: #spaceial case to remove chinease caracters
                to_ret.append("original article wsj article chinese version wsj article english version google translation chinese article chat gpt translation chinese article")
            else:
                d = docs[i]
                to_ret.append(d[:512])
    return to_ret

def save_sentiment(data):
    with open("sentiment.json", "w") as outfile:
        json.dump(data, outfile)

def load_sentiment():
    with open("sentiment.json", "r") as f:
        return json.load(f)


##################################################
# Sentiment analyser
def main ():
    #https://huggingface.co/siebert/sentiment-roberta-large-english/tree/main
    tokenizer = AutoTokenizer.from_pretrained("siebert/sentiment-roberta-large-english")
    model = AutoModelForSequenceClassification.from_pretrained("siebert/sentiment-roberta-large-english")
    sentiment_classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    print("loaded sentiment_classifier")


    data = load_filtered_docs()
    results = None
    try:
        results = load_sentiment()
        print("loaded {} results".format(len(results)))
    except:
        print("result bad loading null set")
        results = {}

    for i in range(0,len(data)):
        try:
            print(i)
            if i in results:
                raise Exception(f"{i} in results already")
            results[i] = sentiment_classifier( data[i] )
            #print(results)
        except:
            save_sentiment(results)
            break
    save_sentiment(results)



##################################################
# Calc what people feel about it

def calc_sentiment_topic():
    topics = load_topics()
    probs = un_pickelize("probs")
    results = load_sentiment()
    print("loaded results")

    topic_sentiments = [ 0 for x in range(len(probs[0]))] #list lenght of topics
    abs_sentiments = [ 0 for x in range(len(probs[0]))] #list lenght of topics

    for i in range(len(probs)): #loop through dock sentiment
        doc_sent = 1 if results[str(i)][0]["label"] == "POSITIVE" else -1
        doc_topic_probs = probs[i]
        for j in range(len(probs[0])): #loop over each topic
            topic_sentiments[j] += doc_sent * doc_topic_probs[j]
            abs_sentiments[j] += abs(doc_sent * doc_topic_probs[j])

    with open(f"sentiment.txt", "w") as outfile:
        for i in range(len(probs[0])):
            tilt = round(  (topic_sentiments[i] / abs_sentiments[i])*100, 1 )
            outfile.write("{:2} {:19} //{:19} {:5}% -- {}\n".format(i, topic_sentiments[i], abs_sentiments[i], tilt,  topics[i][1]))

if __name__ == "__main__":
    #main()
    calc_sentiment_topic()

    #"POSITIVE"
    #"NEGATIVE"
    #"label"
