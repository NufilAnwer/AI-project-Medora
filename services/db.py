from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.medora_db

patients_col = db.patients
doctors_col = db.doctors
records_col = db.records
documents_col = db.documents
users_col = db.users
messages_col = db.messages
prescriptions_col = db.prescriptions