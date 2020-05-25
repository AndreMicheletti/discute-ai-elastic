import sys
import os
import firebase_admin
from elasticsearch import Elasticsearch
from firebase_admin import credentials
from firebase_admin import firestore


def printf(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


# SETUP ELASTIC SEARCH

ELASTIC_SEARCH_URL = os.getenv("ELASTICSEARCH_URL")
COLLECTION_NAME = "definitions"

es = Elasticsearch(ELASTIC_SEARCH_URL)
printf(es.cat.count())
printf("CONNECTED TO ELASTIC")

# FIREBASE START
cred = credentials.Certificate("creds/discute-ai-firebase-adminsdk-3wsyf-82457e075b.json")
app = firebase_admin.initialize_app(cred)

# POPULATE ELASTIC SEARCH
db = firestore.client()
printf("CONNECTED TO FIREBASE")

definitions_ref = db.collection(u'definitions')

printf("FETCHING DOCUMENTS FROM FIREBASE...")
docs = definitions_ref.stream()
docs = list(docs)
n_docs = len(docs)
printf(f"FETCHED {n_docs} DOCS...")

printf("STARTING MIGRATION")
i = 1
for doc in docs:
    res = es.index(index=COLLECTION_NAME, id=doc.id, body=doc.to_dict())
    i += 1
    printf(f"{i}/{n_docs + 1} done")

es.indices.refresh(index=COLLECTION_NAME)
