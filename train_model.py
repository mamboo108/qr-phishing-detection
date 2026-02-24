import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

df = pd.read_csv("qr_features.csv")

print("Dataset balance:")
print(df["label"].value_counts())

X = df.drop("label",axis=1)
y = df["label"].map({"benign":0,"malicious":1})

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

model = RandomForestClassifier(n_estimators=200)
model.fit(X_train,y_train)

pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test,pred))
print("AUC:", roc_auc_score(y_test,prob))

pickle.dump(model, open("qr_model.pkl","wb"))
print("✅ qr_model.pkl saved")