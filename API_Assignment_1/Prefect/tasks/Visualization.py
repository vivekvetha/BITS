# Univariate, bivariate, and multivariate visualization — US population survey data
# Univariate / bivariate / multivariate plots for US population survey (income) data.

import pandas as pd
import io
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from EDA import OUTPUT_DIR, PROCESSED_CSV

sns.set_theme()

df = pd.read_csv(PROCESSED_CSV)
df["Sex"] = df["Sex"].str.strip()
print(df.index)

# Swarm/strip plots are slow on full census-scale rows; use a fixed sample for those plots only
_df_sample = df.sample(n=min(800, len(df)), random_state=42)

# --------------------------------------- UNIVARIATE ANALYSIS ------------------------------

# 1.1 Box Plot
sns.boxplot(x=df["age"])
plt.title("1. Box Plot of Age")
# Save the plot to a buffer
buf_1 = io.BytesIO()
plt.savefig(buf_1, format="png")
buf_1.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_1.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"BoxPlot_Age_{formatted}.png")
# Close the buffer
buf_1.close()
plt.clf()  # Clear the figure so Plot 1 doesn't bleed into Plot 2

# 1.2 Strip plot — distribution of a single continuous variable
sns.stripplot(y=_df_sample["age"])
plt.title("2. Strip Plot of Age (sample)")
# Save the plot to a buffer
buf_2 = io.BytesIO()
plt.savefig(buf_2, format="png")
buf_2.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_2.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"StripPlot_Age_{formatted}.png")
# Close the buffer
buf_2.close()
plt.clf()  # Clear the figure

# 1.3 Swarm Plot — spread of continuous values
sns.swarmplot(x=_df_sample["age"])
plt.title("3. Swarm Plot of Age (sample)")
# Save the plot to a buffer
buf_3 = io.BytesIO()
plt.savefig(buf_3, format="png")
buf_3.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_3.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"SwarmPlot_Age_{formatted}.png")
# Close the buffer
buf_3.close()
plt.clf()  # Clear the figure

sns.swarmplot(x=_df_sample["workhours"])
plt.title("4. Swarm Plot of Work Hours per Week (sample)")
# Save the plot to a buffer
buf_4 = io.BytesIO()
plt.savefig(buf_4, format="png")
buf_4.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_4.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"SwarmPlot_WorkHoursPerWeek_{formatted}.png")
# Close the buffer
buf_4.close()
plt.clf()  # Clear the figure

# 1.4 Histograms
plt.hist(df["age"])
plt.title("5. Histogram of Age")
# Save the plot to a buffer
buf_5 = io.BytesIO()
plt.savefig(buf_5, format="png")
buf_5.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_5.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"Histogram_Age_{formatted}.png")
# Close the buffer
buf_5.close()
plt.clf()  # Clear the figure

# 1.5 Histogram + optional KDE (replaces deprecated sns.distplot)
sns.histplot(df["age"], kde=False, color="blue", bins=5)
plt.title("6. Histogram of Age with 5 bins")
# Save the plot to a buffer
buf_6 = io.BytesIO()
plt.savefig(buf_6, format="png")
buf_6.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_6.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"Histogram_AgeWith5Bins_{formatted}.png")
# Close the buffer
buf_6.close()
plt.clf()  # Clear the figure

# 1.6 Count plot — categorical variable
sns.countplot(data=df, x="Sex")
plt.title("7. Count Plot of Sex (Categorical)")
# Save the plot to a buffer
buf_7 = io.BytesIO()
plt.savefig(buf_7, format="png")
buf_7.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_7.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"CountPlot_Sex_{formatted}.png")
# Close the buffer
buf_7.close()
plt.clf()  # Clear the figure

# --------------------------------------- BIVARIATE ANALYSIS -----------------------------

# 2.1 Boxplot — income outcome vs weekly work hours
sns.boxplot(data=df, x="outcome", y="workhours")
plt.title("8. Box Plot of Income Outcome vs Work Hours per Week")
# Save the plot to a buffer
buf_8 = io.BytesIO()
plt.savefig(buf_8, format="png")
buf_8.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_8.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"BoxPlot_IncomeOutcome_WorkHoursPerWeek_{formatted}.png")
# Close the buffer
buf_8.close()
plt.clf()  # Clear the figure

# 2.2 Scatter Plot
sns.scatterplot(data=df, x="workhours", y="age")
plt.title("9. Scatter Plot of Work Hours vs Age")
# Save the plot to a buffer
buf_9 = io.BytesIO()
plt.savefig(buf_9, format="png")
buf_9.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_9.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"ScatterPlot_WorkHours_Age_{formatted}.png")
# Close the buffer
buf_9.close()
plt.clf()  # Clear the figure

sns.scatterplot(data=df, x="workhours", y="age", hue="outcome")
plt.title("10. Scatter Plot of Work Hours vs Age vs Income Outcome (hue)")
# Save the plot to a buffer
buf_10 = io.BytesIO()
plt.savefig(buf_10, format="png")
buf_10.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_10.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"ScatterPlot_WorkHours_Age_IncomeOutcome_{formatted}.png")
# Close the buffer
buf_10.close()
plt.clf()  # Clear the figure

# 2.3 FacetGrid — Sex vs education level (numeric)
g = sns.FacetGrid(df, col="Sex", height=6.5, aspect=0.85)
g.map(sns.histplot, "education-num")
plt.suptitle("11. Facet Grid of Sex vs Education (years)", y=1.02)
# Save the plot to a buffer
buf_11 = io.BytesIO()
plt.savefig(buf_11, format="png")
buf_11.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_11.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"FacetGrid_Sex_Education_{formatted}.png")
# Close the buffer
buf_11.close()
plt.clf()  # Clear the figure

# ----------------------------- MULTIVARIATE ANALYSIS ----------------------------------

# Income outcome vs Age vs Sex
g = sns.FacetGrid(
    df, col="outcome", hue="Sex", margin_titles=True, height=6.5, aspect=0.85
)
g.map(sns.histplot, "age")
plt.suptitle("12. Facet Grid of Sex vs Age vs Income Outcome", y=1.02)
# Save the plot to a buffer
buf_12 = io.BytesIO()
plt.savefig(buf_12, format="png")
buf_12.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_12.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"FacetGrid_Sex_Age_IncomeOutcome_{formatted}.png")
# Close the buffer
buf_12.close()
plt.clf()  # Clear the figure

# 2.4 lmplot
sns.lmplot(data=df, x="age", y="workhours", hue="Sex")
plt.title("13. lmplot of Age vs Work Hours vs Sex (hue)")
# Save the plot to a buffer
buf_13 = io.BytesIO()
plt.savefig(buf_13, format="png")
buf_13.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_13.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"lmplot_Age_WorkHours_Sex_{formatted}.png")
# Close the buffer
buf_13.close()
plt.clf()  # Clear the figure

sns.lmplot(data=df, x="age", y="education-num", hue="Sex")
plt.title("14. lmplot of Age vs Education (years) vs Sex (hue)")
# Save the plot to a buffer
buf_14 = io.BytesIO()
plt.savefig(buf_14, format="png")
buf_14.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_14.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"lmplot_Age_Education_Sex_{formatted}.png")
# Close the buffer
buf_14.close()
plt.clf()  # Clear the figure

sns.lmplot(data=df, x="workhours", y="age", hue="outcome")
plt.title("15. lmplot of Work Hours vs Age vs Income Outcome (hue)")
# Save the plot to a buffer
buf_15 = io.BytesIO()
plt.savefig(buf_15, format="png")
buf_15.seek(0)
# Encode the image in base64 and log it
img_base64 = base64.b64encode(buf_15.read()).decode("utf-8")
# Get current local date and time
now = datetime.now()
# Format the output
formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
# Save the plot as a file
plt.savefig(OUTPUT_DIR / f"lmplot_WorkHours_Age_IncomeOutcome_{formatted}.png")
# Close the buffer
buf_15.close()
