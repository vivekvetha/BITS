# Pearson correlation and scatter plots (encoded Sex / workclass vs workhours) — US population income dataset.
import pandas as pd
from scipy.stats import pearsonr

from EDA import PROCESSED_CSV

# Import your data into Python
df = pd.read_csv(PROCESSED_CSV)

# Encode categorical columns

print("\n Binary Encode categorical columns")
df["Sex"] = df["Sex"].str.strip()
df["gender_encoded"] = df["Sex"].map({"Male": 1, "Female": 0})

print(df["gender_encoded"].head(10))

print("\n Encode categorical columns with multiple categories")
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["workclass_encoded"] = le.fit_transform(df["workclass"])
print(df["workclass_encoded"].head(10))

list0 = df["gender_encoded"]

list1 = df["workclass_encoded"]

list2 = df["workhours"]

# Apply the pearsonr()

corr, _ = pearsonr(list0, list2)
print("Pearson correlation gender_encoded & workhours : %.3f" % corr)


corr, _ = pearsonr(list1, list2)
print("Pearson correlation workclass_encoded & workhours : %.3f" % corr)

# Pearson correlation: if value is +ve  ( Positive correlation)

# Scatter: workclass_encoded vs workhours
from matplotlib import pyplot

pyplot.scatter(list1, list2)
pyplot.xlabel("workclass_encoded")
pyplot.ylabel("workhours")
pyplot.show()
