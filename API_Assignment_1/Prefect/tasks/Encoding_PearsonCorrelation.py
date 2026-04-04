# Pearson correlation after encoding categoricals (Sex, workclass) vs workhours — US population income dataset.
import pandas as pd
import io
import base64
from datetime import datetime
from scipy.stats import pearsonr

from EDA import OUTPUT_DIR, PROCESSED_CSV

# Import your data into Python
df = pd.read_csv(PROCESSED_CSV)


print(
    "\n\n**************************************************************************\n\n"
)

# Encode categorical columns
print("\n Binary Encode categorical columns like Gender Male 1 and Female 0")
df["Sex"] = df["Sex"].str.strip()
df["gender_encoded"] = df["Sex"].map({"Male": 1, "Female": 0})

print(df["gender_encoded"].head(10))

print("\nEncode categorical columns with multiple categories like workclass")
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["workclass_encoded"] = le.fit_transform(df["workclass"])
print(df["workclass_encoded"].head(10))

print(
    "\n\n**************************************************************************\n\n"
)
print(
    "\nPearson Correlation for gender and workhours and workclass and workhours columns"
)

list0 = df["gender_encoded"]

list1 = df["workclass_encoded"]

list2 = df["workhours"]

# Apply the pearsonr()

corr, _ = pearsonr(list0, list2)
print("\nPearson correlation gender_encoded & workhours : %.3f" % corr)


corr, _ = pearsonr(list1, list2)
print("\nPearson correlation workclass_encoded & workhours : %.3f" % corr)
print(
    "\nInterpretation Correlation between gender_encoded and workhours : .207 shows mild positive correlation"
)
# Pearson correlation: if value is +ve  ( Positive correlation)

# Scatter: gender_encoded vs workhours
from matplotlib import pyplot

pyplot.scatter(list0, list2)
pyplot.xlabel("gender_encoded")
pyplot.ylabel("workhours")

# Save the plot to a buffer
buf = io.BytesIO()
pyplot.savefig(buf, format="png")
buf.seek(0)

# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf.read()).decode("utf-8")

# Get current local date and time
now = datetime.now()

# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")

# Save the plot as a file
pyplot.savefig(OUTPUT_DIR / f"Encoding_PearsonCorrelation_{formatted}.png")

# Close the buffer
buf.close()
