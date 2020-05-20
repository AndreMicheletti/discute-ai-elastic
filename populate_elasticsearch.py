import firebase_admin
from elasticsearch import Elasticsearch
from firebase_admin import credentials
from firebase_admin import firestore

# SETUP ELASTIC SEARCH
ELASTIC_SEARCH_URL = "localhost:9002"
COLLECTION_NAME = "definitions"

es = Elasticsearch()

# FIREBASE START
cred = credentials.Certificate("creds/discute-ai-firebase-adminsdk-3wsyf-82457e075b.json")
app = firebase_admin.initialize_app(cred)

# POPULATE ELASTIC SEARCH
db = firestore.client()

definitions_ref = db.collection(u'definitions')
docs = definitions_ref.stream()

for doc in docs:
    res = es.index(index=COLLECTION_NAME, id=doc.id, body=doc.to_dict())

es.indices.refresh(index=COLLECTION_NAME)
