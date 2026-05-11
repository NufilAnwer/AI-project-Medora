import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

df = pd.read_csv("data/heart.csv")
label_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
label_encoders = {}

for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df.drop('HeartDisease', axis=1)
y = df['HeartDisease']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

xgb_temp = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_temp.fit(X_train, y_train)
importances = pd.Series(xgb_temp.feature_importances_, index=X.columns)
top_features = importances.sort_values(ascending=False).head(5).index.tolist()

X_train_sel = pd.DataFrame(X_train, columns=X.columns)[top_features]
X_test_sel = pd.DataFrame(X_test, columns=X.columns)[top_features]

xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb.fit(X_train_sel, y_train)

def predict_heart_disease(user_input):
    input_df = pd.DataFrame([user_input])
    for col in label_cols:
        if col in input_df.columns and col in label_encoders:
            input_df[col] = label_encoders[col].transform(input_df[col])
    for col in X.columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df_ordered = input_df[X.columns]
    input_df_scaled = scaler.transform(input_df_ordered)
    input_df_scaled = pd.DataFrame(input_df_scaled, columns=X.columns)[top_features]
    prediction = xgb.predict(input_df_scaled)[0]
    return "High Risk" if prediction == 1 else "Low Risk"
