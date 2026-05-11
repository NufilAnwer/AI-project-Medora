import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

df = pd.read_csv("data/family_history_rare_disease_cleaned.csv")
cat_cols = ['Gender','Parental History','Sibling History',
            'Known Genetic Mutation','Early Onset Cases in Family',
            'Environmental Risk Exposure','geneticTest']

encoders = {c: LabelEncoder().fit(df[c]) for c in cat_cols}
for c, le in encoders.items():
    df[c] = le.transform(df[c])

X = df.drop(['Patient ID', 'geneticTest'], axis=1)
y = df['geneticTest']

X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
X_tr, X_te, y_tr, y_te = train_test_split(X_res, y_res, test_size=0.2, random_state=42, stratify=y_res)

pos_ratio = y_tr.sum() / len(y_tr)
clf = XGBClassifier(
    n_estimators=400, learning_rate=0.05, max_depth=5,
    subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
    scale_pos_weight=(1-pos_ratio)/pos_ratio, random_state=42, n_jobs=-1,
    eval_metric='logloss'
)
clf.fit(X_tr, y_tr)

def predict_genetic_test(user_input):
    input_df = pd.DataFrame([user_input])
    for col in cat_cols[:-1]:  
        if col in input_df.columns and col in encoders:
            input_df[col] = encoders[col].transform(input_df[col])
    for col in X.columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[X.columns]
    prediction = clf.predict(input_df)[0]
    return "Genetic Test Recommended" if prediction == 1 else "No Genetic Test Needed"
