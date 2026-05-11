import uuid
from datetime import datetime

def gen_id(prefix="id_"):
    return prefix + str(uuid.uuid4())[:8]

class User:
    def __init__(self, user_id, name, email, role):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role

class Patient(User):
    def __init__(self, user_id, name, email, role, dob=None):
        super().__init__(user_id, name, email, role)
        self.dob = dob
        self.records = []
        self.documents = []

    def add_record(self, record):
        self.records.append(record)

    def add_document(self, doc):
        self.documents.append(doc)

class Doctor(User):
    def __init__(self, user_id, name, email, role, specialization):
        super().__init__(user_id, name, email, role)
        self.specialization = specialization
        self.patients = []

    def add_patient(self, patient):
        self.patients.append(patient)

class HealthRecord:
    def __init__(self, record_id, timestamp, weight_kg, height_m, blood_pressure, heart_rate):
        self.record_id = record_id
        self.timestamp = timestamp
        self.weight_kg = weight_kg
        self.height_m = height_m
        self.blood_pressure = blood_pressure
        self.heart_rate = heart_rate

class MedicalDocument:
    def __init__(self, doc_id, title, source, file_data, file_type, timestamp=None):
        self.doc_id = doc_id
        self.title = title
        self.source = source
        self.file_data = file_data
        self.file_type = file_type
        self.timestamp = timestamp or datetime.now()

    def __repr__(self):
        return f"<MedicalDocument {self.doc_id} | {self.title} | {self.timestamp}>"

class NERExtractor:
    def extract(self, text):
        return {"entities": ["example_entity"]}

class Summarizer:
    def summarize(self, text):
        return "This is a summary."

class RiskPredictor:
    def predict(self, record):
        return "Low Risk" if record.heart_rate < 100 else "High Risk"

class RAGRetriever:
    def __init__(self):
        self.index = []

    def add_document(self, doc):
        self.index.append(doc)

    def retrieve(self, query):
        return f"Retrieved info for: {query}"

class ChatbotEngine:
    def __init__(self, retriever, ner, summarizer, predictor):
        self.retriever = retriever
        self.ner = ner
        self.summarizer = summarizer
        self.predictor = predictor

    def ask(self, user, query):
        entities = self.ner.extract(query)
        info = self.retriever.retrieve(query)
        summary = self.summarizer.summarize(info)
        return {"reply": f"Entities: {entities['entities']}, Summary: {summary}"}

class Dashboard:
    def generate_summary(self, patient):
        total_docs = len(patient.documents)
        total_records = len(patient.records)
        last_record = patient.records[-1] if patient.records else None
        return {
            "Total Documents": total_docs,
            "Total Records": total_records,
            "Last Heart Rate": last_record.heart_rate if last_record else "N/A"
        }
