# Chi-square test of independence (Sex vs workclass) — US population income dataset.
import pandas as pd

from EDA import PROCESSED_CSV

print(
    "\n\n**************************************************************************\n\n"
)
df = pd.read_csv(PROCESSED_CSV)

# To explore the correlation between Gender and workclass in the dataset
print(
    "\n Explore the ChiSquare correlation between Gender and workclass in the dataset "
)
new = df.groupby(["workclass", "Sex"]).size()
print(new)

# Federal-gov - 18 [female], 31[male]
# local-gov - 47[female], 87 male]
# Private-  444	female], 911 [male]
# Self-emp-inc - 11 [female], 63 [male]
# Self-emp-not-inc - 22 [female], 131 [male]
# State-gov  - 25 [female], 50 [male]


from scipy.stats import chi2_contingency

data = [18, 47, 444, 11, 22, 25], [31, 87, 911, 63, 131, 50]
print("\n data for chi square test  Female and Male	vs workclass: ", data)
stat, p, dof, expected = chi2_contingency(data)

## interpret p-value
alpha = 0.05
print("p value is " + str(p))
if p <= alpha:
    print("Gender and workclass are Dependent (reject H0)")
else:
    print("Gender and workclass are Independent (H0 holds true)")

# Output: p value is 4.106490998765035e-06
# alpha of 0.05 > p value of 4.106490998765035e-06; Dependent (reject H0)
