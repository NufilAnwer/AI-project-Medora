import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

df = pd.read_csv("data/StressLevelDataset.csv")

X = df[["self_esteem", "blood_pressure", "sleep_quality", "bullying"]]
y = df["stress_level"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=4)
model.fit(X_train, y_train)

def map_self_esteem(category):
    return {'low': 10, 'mild': 20, 'severe': 27}.get(category.lower(), 15)

def map_blood_pressure(category):
    return {'low': 1, 'normal': 2, 'high': 3}.get(category.lower(), 2)

def map_sleep_quality(category):
    return {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}.get(category.lower(), 3)

def map_bullying(category):
    return {'none': 0, 'mild': 1, 'moderate': 2, 'severe': 3, 'extreme': 5}.get(category.lower(), 2)

stress_map = {
    0: "Low stress — you're doing great!",
    1: "Mild stress — consider improving sleep and reducing pressure.",
    2: "Severe stress — please consult a mental health professional."
}

def predict_stress(self_esteem, blood_pressure, sleep_quality, bullying):
    features = pd.DataFrame([[
        map_self_esteem(self_esteem),
        map_blood_pressure(blood_pressure),
        map_sleep_quality(sleep_quality),
        map_bullying(bullying)
    ]], columns=["self_esteem", "blood_pressure", "sleep_quality", "bullying"])

    prediction = model.predict(features)[0]
    return {
        "level": int(prediction),
        "message": stress_map.get(prediction, "Unknown stress level")
    }
