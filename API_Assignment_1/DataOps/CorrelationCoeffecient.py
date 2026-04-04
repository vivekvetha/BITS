import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from EDA import PROCESSED_CSV

print(
    "\n\n**************************************************************************\n\n"
)

print("\nCorrelation Matrix - Internally uses Pearson Correlation")
df = pd.read_csv(PROCESSED_CSV)
# print(df)

# remove leading and trailing spaces from string columns
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print("\nEncoding categorical columns in the entire dataframe using factorize")
# encode categorical columns in the entire dataframe using factorize

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = pd.factorize(df[col])[0]


# Correlation Matrix - Internally uses Pearson Correlation
cor = df.corr()

# Plotting Heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(cor, annot=True)
plt.show()
