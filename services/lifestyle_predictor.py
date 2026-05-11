import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

np.random.seed(42)
num_samples = 500

data = {
    'age': np.random.randint(18, 70, num_samples),
    'gender': np.random.randint(0, 2, num_samples),
    'weight': np.random.randint(45, 100, num_samples),
    'height': np.round(np.random.uniform(1.5, 2.0, num_samples), 2),
    'activity_level': np.random.randint(1, 6, num_samples),
    'sleep_hours': np.round(np.random.uniform(4, 9, num_samples), 1),
    'diet_score': np.random.randint(1, 5, num_samples)
}

df = pd.DataFrame(data)

df['sleep_issue'] = (df['sleep_hours'] < 6).astype(int)
df['activity_issue'] = (df['activity_level'] < 3).astype(int)
df['diet_issue'] = (df['diet_score'] < 3).astype(int)
df['maintain_lifestyle'] = ((df['sleep_hours'] >= 6) & (df['activity_level'] >= 3) & (df['diet_score'] >= 3)).astype(int)

X = df[['age', 'gender', 'weight', 'height', 'activity_level', 'sleep_hours', 'diet_score']].values
y = df[['sleep_issue', 'activity_issue', 'diet_issue', 'maintain_lifestyle']].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(4, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=16, verbose=0)

recommendation_map = ["Improve sleep", "Increase activity", "Adjust diet", "Maintain lifestyle"]

def predict_lifestyle(age, gender, weight, height, activity_level, sleep_hours, diet_score):
    gender_val = 0 if gender.upper() == "M" else 1
    user_input = np.array([[age, gender_val, weight, height, activity_level, sleep_hours, diet_score]])
    user_input_scaled = scaler.transform(user_input)
    pred = model.predict(user_input_scaled)[0]
    recommendations = [recommendation_map[i] for i, val in enumerate(pred) if val > 0.5]
    return {
        "probabilities": pred.tolist(),
        "recommendations": recommendations
    }
