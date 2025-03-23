import pandas as pd
import joblib
import os
import traceback
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score

# 1️⃣ Load and prepare data
try:
    dataset_path = os.path.join("datasets", "thyroid.csv")
    df = pd.read_csv(dataset_path)
    print("✅ Dataset loaded successfully!")
except FileNotFoundError:
    print(f"⚠️ Error: 'thyroid.csv' not found in {dataset_path}!")
    exit()

# 2️⃣ Split and preprocess data
X = df.drop(columns=["Condition"])
y = df["Condition"]

# Encode target variable
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3️⃣ Train model
print("🚀 Training model...")
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'  # Handle class imbalance
)
model.fit(X_train_scaled, y_train)

# 4️⃣ Evaluate model
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2f}")

# 5️⃣ Save full pipeline
models_folder = "models"
os.makedirs(models_folder, exist_ok=True)

pipeline = {
    'model': model,
    'scaler': scaler,
    'encoder': le,
    'feature_names': X.columns.tolist(),
    'class_names': list(le.classes_)
}

try:
    model_path = os.path.join(models_folder, "thyroid_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"✅ Full pipeline saved to: {model_path}")
    print("Saved components:", list(pipeline.keys()))
except Exception as e:
    print(f"⚠️ Error saving pipeline: {e}")
    traceback.print_exc()

# 🎉 Done!
print("✅ All done — pipeline trained and saved!")