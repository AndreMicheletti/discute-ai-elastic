from urllib.parse import unquote_plus

from elasticsearch import Elasticsearch
from fastapi import FastAPI

app = FastAPI()
es = Elasticsearch()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/definitions")
async def get_all_definitions():

    es_query = {
        "query": {
            "match_all": {}
        }
    }
    res = es.search(index="definitions", body=es_query)

    if "hits" in res.keys() and not res["timed_out"]:
        return res["hits"]["hits"]

    return {"error": "server error"}, 500


@app.get("/definitions/{search_tag_encoded}")
async def get_all_definitions(search_tag_encoded: str):

    search_tag = unquote_plus(search_tag_encoded)

    es_query = {
      "query": {
        "match": {
          "title": {
            "query": search_tag,
            "fuzziness": "1"
          }
        }
      }
    }
    res = es.search(index="definitions", body=es_query)

    if "hits" in res.keys() and not res["timed_out"]:
        return res["hits"]["hits"]

    return {"error": "server error"}, 500
