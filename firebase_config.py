import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("integra-tech-firebase-adminsdk-fbsvc-eae48ae410.json")

firebase_admin.initialize_app(cred)

db = firestore.client()

