# Discretization by Binning methods
# Distance Binning

import pandas as pd
import numpy as np

from EDA import PROCESSED_CSV

# pd.set_option('display.max_rows', None)

df = pd.read_csv(PROCESSED_CSV)
# print(df)

print(
    "\n\n**************************************************************************\n\n"
)

print("\n Distance Binning for Age column print min and max values")
# 1. Distance binning
# Formula -> interval = (max-min) / Number of Bins
# Let us consider the 'Age' continuous value column for binning
min_value = df["age"].min()
max_value = df["age"].max()
print(min_value)
print(max_value)

# Suppose the bin size is 4 then the interval will be (92-1)/4 = 22.75
# linspace returns evenly spaced numbers over a specified interval.
# Returns num evenly spaced samples, calculated over the interval [start, stop].
bins = np.linspace(min_value, max_value, 4)
print("\n bins : ", bins)

# 1-23 - Child; till 46 - Adult; till 69 - Middle Age; till 92 - Senior Citizen
print("\n 1-42 young, 43-65 middle age, 65-90 senior citizen")
labels = ["Young", "Middle Age", "Senior Citizen"]

# We can use the cut() function to convert the numeric values of the column Age into the categorical values.
# We need to specify the bins and the labels.
df["bins_dist"] = pd.cut(df["age"], bins=bins, labels=labels, include_lowest=True)
print("\n Distance Binning for Age column")
print(df["bins_dist"])
