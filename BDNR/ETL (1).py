import requests
import pandas as pd 
from pymongo import MongoClient
import hashlib
import requests 
import datetime
import json
import string




timestamp = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
pub_key = '9e54b9779a30de9e828a6e080f580dad'
priv_key = '2b84ffeeca90c76752f652e13528bfa5ed37dfd2'


def hash_params():
    """ Marvel API requires server side API calls to include
    md5 hash of timestamp + public key + private key """

    hash_md5 = hashlib.md5()
    hash_md5.update(f'{timestamp}{priv_key}{pub_key}'.encode('utf-8'))
    hashed_params = hash_md5.hexdigest()

    return hashed_params

params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(),'limit':100};

myclient = MongoClient('localhost', 27017)
mydb = myclient["superheroes"] 
mycol = mydb["marvel_superheroes"] 


dicts=[]
dfs=[]
letras = list(string.ascii_uppercase)
for i in range(len(letras)):
    last = 0
    params = {'ts': timestamp, 'apikey': pub_key, 'hash': hash_params(),'limit':100,'nameStartsWith':letras[i]}
    res = requests.get('https://gateway.marvel.com:443/v1/public/characters',
                params=params)
    results = res.json()
    mycol.insert_many(results['data']['results'])
    dicts.append(results['data']['results'])
    dfs.append(pd.json_normalize(results['data']['results']))
    

dataframe = pd.concat(dfs)
dataframe=dataframe[['id','name','description','comics.available','comics.items','series.available','series.items','stories.available','stories.items','events.available','events.items']]
dataframe.to_csv("Monet_file.csv",index=False)

comics=[]
stories=[]
events=[]
series=[]
superheroes=[]


for i in range(len(dicts)):
    superh=dicts[i]
    with open('superh.json', 'w') as json_file:
        json.dump(superh, json_file)

    with open('superh.json','r') as f:
        data = json.loads(f.read())
    superh = pd.json_normalize(data)
    superh=superh.drop(['comics.items', 'stories.items', 'events.items', 'series.items', 'urls'], axis=1)
    superh=superh.replace(r'^\s*$', 'no description', regex=True)
    comics_superh = pd.json_normalize(data, record_path=['comics','items'], meta=['id'])
    stories_superh = pd.json_normalize(data, record_path=['stories','items'], meta=['id'])
    events_superh = pd.json_normalize(data, record_path=['events','items'], meta=['id'])
    series_superh = pd.json_normalize(data, record_path=['series','items'], meta=['id'])
    comics.append(comics_superh)
    stories.append(stories_superh)
    events.append(events_superh)
    series.append(events_superh)
    superheroes.append(superh)
superh=pd.concat(superheroes)
comics_superh=pd.concat(comics)
stories_superh=pd.concat(stories)
events_superh=pd.concat(events)
series_superh=pd.concat(series)

#taking csvs
superh.to_csv('superhero.csv', header=True, sep='\t', index=False)
comics_superh.to_csv('comic.csv', header=True, sep='\t', index=False)
stories_superh.to_csv('story.csv', header=True, sep='\t', index=False)
events_superh.to_csv('event.csv', header=True, sep='\t', index=False)
series_superh.to_csv('serie.csv', header=True, sep='\t', index=False)

