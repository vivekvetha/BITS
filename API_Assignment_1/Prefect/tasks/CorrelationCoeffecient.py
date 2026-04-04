import pandas as pd
import seaborn as sns
import io
import base64
from datetime import datetime
import matplotlib.pyplot as plt

from EDA import OUTPUT_DIR, PROCESSED_CSV

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
plt.savefig(OUTPUT_DIR / f"CorrelationCoeffecient_{formatted}.png")

# Close the buffer
buf.close()
