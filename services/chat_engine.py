# import random
# import json
# import os
# import re
# import nltk
# import numpy as np
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.linear_model import LogisticRegression

# nltk.download('punkt')

# class MedoraChatbot:
#     def __init__(self, intents_path="data/intents.json"):
#         with open(intents_path, "r", encoding="utf-8") as f:
#             self.intents = json.load(f)["intents"]
#         self.vectorizer = CountVectorizer()
#         self.model = LogisticRegression()
#         self.train()

#     def train(self):
#         patterns = []
#         tags = []
#         for intent in self.intents:
#             for pattern in intent["patterns"]:
#                 patterns.append(pattern)
#                 tags.append(intent["tag"])
#         X = self.vectorizer.fit_transform(patterns)
#         y = tags
#         self.model.fit(X, y)

#     def get_response(self, user_input):
#         X_test = self.vectorizer.transform([user_input])
#         tag = self.model.predict(X_test)[0]
#         for intent in self.intents:
#             if intent["tag"] == tag:
#                 return random.choice(intent["responses"])
#         return "I'm not sure how to help with that. Please consult a doctor."

# chatbot = MedoraChatbot()

#transformeers
#slow model 

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

def get_medora_response(user_input, chat_history=None):
    prompt = f"<|user|> {user_input}\n<|assistant|>"
    output = pipe(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]["generated_text"]
    response = output.split("<|assistant|>")[-1].strip()
    return response