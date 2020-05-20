from fastapi import FastAPI
from elasticsearch import Elasticsearch

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


@app.get("/definitions/{search}")
async def get_all_definitions(search: str):

    es_query = {
        "query": {
            "match_all": {}
        }
    }
    res = es.search(index="definitions", body=es_query)
    return res
