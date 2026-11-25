# ===============================
# 🔹 Train Random Forest Model
# ===============================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
from sklearn.preprocessing import LabelEncoder

# 1️⃣ Load dataset
data = pd.read_csv("pet.csv")  # replace with your CSV filename

# 2️⃣ Encode PetType if it’s a string (e.g., 'Cat', 'Dog')
if data['PetType'].dtype == object:
    le = LabelEncoder()
    data['PetType'] = le.fit_transform(data['PetType'])  # Cat→0, Dog→1

# 3️⃣ Features and target
X = data[['PetType', 'heart_rate', 'temperature', 'spo2']]
y = data['Condition']  # disease label

# 4️⃣ Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5️⃣ Initialize and train Random Forest
rf_model = RandomForestClassifier(
    n_estimators=100, random_state=42
)
rf_model.fit(X_train, y_train)

# 6️⃣ Evaluate the model
y_pred = rf_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 7️⃣ Save the trained model
with open("rf.pkl", "wb") as f:
    pickle.dump(rf_model, f)

print("Model trained and saved as rf.pkl ✅")
