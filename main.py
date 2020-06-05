import os
from urllib.parse import unquote_plus

import firebase_admin
from elasticsearch import Elasticsearch
from fastapi import FastAPI
from firebase_admin import credentials
from firebase_admin import firestore

app = FastAPI()
ELASTIC_SEARCH_URL = os.getenv("ELASTICSEARCH_URL")
es = Elasticsearch(ELASTIC_SEARCH_URL)

# FIREBASE START
cred = credentials.Certificate("creds/discute-ai-firebase-adminsdk-3wsyf-82457e075b.json")
frbase = firebase_admin.initialize_app(cred)
db = firestore.client()


def mock_elastic_return(document):
    return {
        "_index": "definitions",
        "_type": "_doc",
        "_id": document.id,
        "_score": 1,
        "_source": document.to_dict()
    }


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/definitions")
async def get_all_definitions():
    try:
        docs = db.collection(u'definitions') \
            .order_by(u'likes', direction="DESCENDING") \
            .order_by(u'title') \
            .stream()
        return list(map(mock_elastic_return, docs))

    except Exception as e:
        print(e)
        return {"error": "server error"}, 500


@app.get("/definitions/featured")
async def get_all_featured():
    try:
        docs = db.collection(u'definitions') \
            .where(u'featured', u'==', True) \
            .order_by(u'likes', direction="DESCENDING") \
            .order_by(u'title') \
            .stream()
        return list(map(mock_elastic_return, docs))

    except Exception as e:
        print(e)
        return {"error": "server error"}, 500


@app.get("/definitions/tags")
async def get_featured_tags():

    return [
        {"tag": "ideologia", "title": "Ideologia"},
        {"tag": "sistema-politico", "title": "Sistemas Políticos"},
        {"tag": "executivo", "title": "Poder Executivo"},
        {"tag": "judiciario", "title": "Poder Judiciário"},
        {"tag": "legislativo", "title": "Poder Legislativo"},
        {"tag": "ministerio", "title": "Ministérios"},
        {"tag": "brasil", "title": "Brasil"},
        {"tag": "mundo", "title": "Mundo"},
    ]

@app.get("/definitions/tag/{search_tag}")
async def get_all_definitions_by_tag(search_tag: str):
    try:
        docs = db.collection(u'definitions') \
            .where(u'tags', u'array_contains', search_tag) \
            .order_by(u'likes', direction="DESCENDING") \
            .order_by(u'title') \
            .stream()
        return list(map(mock_elastic_return, docs))

    except Exception as e:
        print(e)
        return {"error": "server error"}, 500


@app.get("/definitions/search/{search_tag_encoded}")
async def get_search_definitions(search_tag_encoded: str):

    search_tag = unquote_plus(search_tag_encoded)

    es_query = {
      "query": {
          "query_string": {
              "query": f"*{search_tag}*",
              "fields": ["title^2", "tags", "text"]
          }
      }
    }
    res = es.search(index="definitions", body=es_query)

    if "hits" in res.keys() and not res["timed_out"]:
        return res["hits"]["hits"]

    return {"error": "server error"}, 500
