# Demo of Normalization -> Min-Max Normalization

# Min-max normalization demo on workhours — US population income dataset.
# So age ranges will be in the interval [0,1]

print(
    "\n\n**************************************************************************\n\n"
)

import pandas as pd

from EDA import PROCESSED_CSV

df = pd.read_csv(PROCESSED_CSV)

df.head()

print(" apply normalization techniqueson on wokhours column")
# copy the data
df_normalized = df.copy()

# apply normalization techniques
# for column in df_min_max_scaled.columns:
# new-x = x - min(x) / max(x) - min(x)
df_normalized["workhours"] = (
    df_normalized["workhours"] - df_normalized["workhours"].min()
) / (df_normalized["workhours"].max() - df_normalized["workhours"].min())

print("\n normalized data:")
print(df_normalized.head(10))
