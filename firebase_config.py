import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("integra-tech-firebase-adminsdk-fbsvc-91088353d7.json")

firebase_admin.initialize_app(cred)

db = firestore.client()
