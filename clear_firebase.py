import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# FIREBASE START
cred = credentials.Certificate("creds/discute-ai-firebase-adminsdk-3wsyf-82457e075b.json")
app = firebase_admin.initialize_app(cred)

# POPULATE ELASTIC SEARCH
db = firestore.client()
print("CONNECTED TO FIREBASE")

db.collection(u'definitions')