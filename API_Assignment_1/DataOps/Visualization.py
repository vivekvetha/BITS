# Univariate, bivariate, and multivariate visualization — US population survey data
# Univariate / bivariate / multivariate plots for US population survey (income) data.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from EDA import PROCESSED_CSV

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
plt.show()

# 1.2 Strip plot — distribution of a single continuous variable
sns.stripplot(y=_df_sample["age"])
plt.title("2. Strip Plot of Age (sample)")
plt.show()

# 1.3 Swarm Plot — spread of continuous values
sns.swarmplot(x=_df_sample["age"])
plt.title("3. Swarm Plot of Age (sample)")
plt.show()

sns.swarmplot(x=_df_sample["workhours"])
plt.title("4. Swarm Plot of Work Hours per Week (sample)")
plt.show()

# 1.4 Histograms
plt.hist(df["age"])
plt.title("5. Histogram of Age")
plt.show()

# 1.5 Histogram + optional KDE (replaces deprecated sns.distplot)
sns.histplot(df["age"], kde=False, color="blue", bins=5)
plt.title("6. Histogram of Age with 5 bins")
plt.show()

# 1.6 Count plot — categorical variable
sns.countplot(data=df, x="Sex")
plt.title("7. Count Plot of Sex (Categorical)")
plt.show()

# --------------------------------------- BIVARIATE ANALYSIS -----------------------------

# 2.1 Boxplot — income outcome vs weekly work hours
sns.boxplot(data=df, x="outcome", y="workhours")
plt.title("8. Box Plot of Income Outcome vs Work Hours per Week")
plt.show()

# 2.2 Scatter Plot
sns.scatterplot(data=df, x="workhours", y="age")
plt.title("9. Scatter Plot of Work Hours vs Age")
plt.show()

sns.scatterplot(data=df, x="workhours", y="age", hue="outcome")
plt.title("10. Scatter Plot of Work Hours vs Age vs Income Outcome (hue)")
plt.show()

# 2.3 FacetGrid — Sex vs education level (numeric)
g = sns.FacetGrid(df, col="Sex", height=6.5, aspect=0.85)
g.map(sns.histplot, "education-num")
plt.suptitle("11. Facet Grid of Sex vs Education (years)", y=1.02)
plt.show()

# ----------------------------- MULTIVARIATE ANALYSIS ----------------------------------

# Income outcome vs Age vs Sex
g = sns.FacetGrid(
    df, col="outcome", hue="Sex", margin_titles=True, height=6.5, aspect=0.85
)
g.map(sns.histplot, "age")
plt.suptitle("12. Facet Grid of Sex vs Age vs Income Outcome", y=1.02)
plt.show()

# 2.4 lmplot
sns.lmplot(data=df, x="age", y="workhours", hue="Sex")
plt.title("13. lmplot of Age vs Work Hours vs Sex (hue)")
plt.show()

sns.lmplot(data=df, x="age", y="education-num", hue="Sex")
plt.title("14. lmplot of Age vs Education (years) vs Sex (hue)")
plt.show()

sns.lmplot(data=df, x="workhours", y="age", hue="outcome")
plt.title("15. lmplot of Work Hours vs Age vs Income Outcome (hue)")
plt.show()
