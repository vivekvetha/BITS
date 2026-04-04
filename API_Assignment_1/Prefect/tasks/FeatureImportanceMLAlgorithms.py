import pandas as pd
import io
import base64
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from EDA import OUTPUT_DIR, PROCESSED_CSV

print(
    "\n\n**************************************************************************\n\n"
)
print("\nFeature Importance Analysis")

# Load Dataset
df = pd.read_csv(PROCESSED_CSV)

print("Initial Dataset Shape:", df.shape)

# -------------------------------------------------
# DATA PREPROCESSING
# -------------------------------------------------
print(
    "\n Data Preprocessing: Dropping unnecessary columns and encoding categorical variables"
)
print(
    "\n Dropping columns: censor-sample, education, relationship, capital-gain, capital-loss"
)
# Drop date columns (not used directly in ML unless engineered)
df = df.drop(
    ["censor-sample", "education", "relationship", "capital-gain", "capital-loss"],
    axis=1,
)
print("\nColumns to process\n")
print(df.columns)

# Convert categorical columns
# df = pd.get_dummies(df, columns=['Gender'], drop_first=True)

# Encode Target Variable (DischargeType)
print("\n Encode categorical columns with multiple categories")

# remove leading and trailing spaces from string columns
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
# encode categorical columns in the entire dataframe using factorize

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = pd.factorize(df[col])[0]
# print("\nProcessed Columns:\n", df.columns)
print(df.head(10))


# Feature & Target Selection
X = df[
    [
        "age",
        "workclass",
        "education-num",
        "marital-status",
        "occupation",
        "race",
        "Sex",
        "workhours",
        "Country",
    ]
]

y = df["outcome"]

# -------------------------------------------------
# 1️⃣ Decision Tree - CART Feature Importance
# -------------------------------------------------

from sklearn.tree import DecisionTreeClassifier

dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X, y)

dt_importance = dt_model.feature_importances_

print("\nDecision Tree Feature Importance")
for name, score in zip(X.columns, dt_importance):
    print(f"{name} : {score:.4f}")

plt.figure()
plt.bar(X.columns, dt_importance)
plt.title("Decision Tree Feature Importance")
plt.xticks(rotation=45)

# Save the plot to a buffer
buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)

# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf.read()).decode("utf-8")

# Get current local date and time
now = datetime.now()

# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")

# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"DecisionTree_{formatted}.png")

# Close the buffer
buf.close()
plt.clf()  # Clear the figure

# -------------------------------------------------
# 2️⃣ Random Forest Feature Importance
# -------------------------------------------------

from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X, y)

rf_importance = rf_model.feature_importances_

print("\nRandom Forest Feature Importance")
for name, score in zip(X.columns, rf_importance):
    print(f"{name} : {score:.4f}")

plt.figure()
plt.bar(X.columns, rf_importance)
plt.title("Random Forest Feature Importance")
plt.xticks(rotation=45)

# Save the plot to a buffer
buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)

# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf.read()).decode("utf-8")

# Get current local date and time
now = datetime.now()

# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")

# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"RandomForest_{formatted}.png")

# Close the buffer
buf.close()

# Final Conclusion
# Age, education-num , marital-status occupation and workhours are  features most important in this dataset
print(
    "\nFinal Conclusion:\nAge, education-num , marital-status occupation and workhours are  features most important in this dataset"
)
