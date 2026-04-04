import pandas as pd

from EDA import PROCESSED_CSV, RAW_CSV

# Load the dataset — treat "?" and empty strings as missing (defaults still apply)
df = pd.read_csv(RAW_CSV, na_values=["?", ""], skipinitialspace=True)
print(df)
print("\nDataframe Info:")
print(df.shape)

# Summary statistics
print("\nSummary Statistics:")
print(df.describe(include="all"))

# Checking for missing values
print("\nMissing Values:")
print(df.isnull().sum())
print(df[df.isnull().any(axis=1)])

# Missing values in selected columns (column name)
categorical_cols = ["workclass", "occupation", "Country"]
for col in categorical_cols:
    print(f"\nMissing Values in {col}:")
    n_missing = df[col].isnull().sum()
    print(f"Number of missing values in {col}: {n_missing}")

# Mode imputation for categoricals (missing values were read as NaN from "?" / empty)
print("\nMode imputation:")
for col in categorical_cols:
    if not df[col].isnull().any():
        continue
    mode_value = df[col].mode()[0]
    n_missing = df[col].isnull().sum()
    df[col] = df[col].fillna(mode_value)
    print(f"  {col}: filled {n_missing} values with mode {mode_value!r}")

# remove missing values as these are
# print("Delete all rows with  missing values  as these are categorical variables")
# df.dropna(inplace=True)

df.to_csv(PROCESSED_CSV, index=False)
df1 = pd.read_csv(PROCESSED_CSV)


# Checking for missing values
print("\nCheck new CSV file for missing values in DF1:")
print(df1.isnull().sum())
print("\nCheck shape of Processed CSV:")
print(df1.shape)
