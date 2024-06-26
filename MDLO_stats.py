from utils import *
from groupings import *
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel


stimulus = "Direction"
alternative = "right"
scipy_alternative = SCIPY_ALTS[alternative]
patients_excluded = []
dose_group = "all" # "1", "2", "3", "4", or "all"
patient_group = "all" # "low-vision", "tunnel-vision", or "all"
datafile = "low-doses-MDLO.xlsx"
BUMP_CHANCE = True
chance = 0.5

# Load and preprocess data
data = pd.read_excel(datafile, sheet_name=stimulus)
data = data[~data["Patient"].isin(patients_excluded)]
data["Before_After"] = data["Visit"].apply(lambda x: "Baseline" if x == "Baseline" else "Post-Treatment")
data["Patient_group"] = data["Patient"].map(PATIENT_GROUPS)
data["Dose_group"] = data["Patient"].map(DOSE_GROUPS)
if dose_group != "all":
    data = data[data["Dose_group"] == dose_group]
if patient_group != "all":
    data = data[data["Patient_group"] == patient_group]

data = data.groupby(["Patient", "Before_After"]).agg(
    {
        "N correct": "sum",
        "N total": "sum"
    }
)
data["Mean_accuracy"] = data["N correct"] / data["N total"]

patient_baselines = pd.DataFrame(data.query("Before_After == 'Baseline'")["Mean_accuracy"])\
                                .reset_index()
patient_baselines = patient_baselines.drop(columns=["Before_After"])\
                                        .rename(columns={"Mean_accuracy": "Null_mean"})
data = pd.merge(data.reset_index(), patient_baselines, on=["Patient"], how="left")

'''
Like in the standard error of the mean (SEM) in a Gaussian distribution, 
the binomial error is the standard deviation of the binomial distribution   
divided by the number of trials. 

std err (gaussian = std / sqrt(n) = sqrt( std^2 / n)
std(binomial) = sqrt( n * p * (1-p)) 
std err (bin) = std(binomial) / n = sqrt( p * (1-p) / n)
'''


data = df_binomial_error(data, "Mean_accuracy", "N total")

if BUMP_CHANCE:
    data = bump_to_chance(data, "Null_mean", chance)
    data = bump_to_chance(data, "Mean_accuracy", chance)

# Use the baseline mean accuracy as the null hypothesis
diffs = data[data["Before_After"] == "Baseline"].merge(data[data["Before_After"] == "Post-Treatment"], on="Patient",
                                                        suffixes=("_before", "_after"),
                                                        how="outer")
diffs["Improvement on %s"%stimulus] = diffs["Mean_accuracy_after"] - diffs["Mean_accuracy_before"]
diffs = diffs[["Patient", "Improvement on %s"%stimulus]].fillna(0)

mean_improvement, std_improvement, sem_improvement, _ = mean_and_sem(diffs, "Improvement on %s"%stimulus, verbose=True)
print ("Paired %s sample improvement in (n=%d patients) on "%(alternative, diffs.shape[0]), stimulus, "\n" + "="*150)
print (diffs.to_string())
print (ttest_rel(diffs["Improvement on %s"%stimulus].values, [0] * diffs.shape[0], alternative=scipy_alternative), "\n" + "="*150)

data = t_test_df(data, "Mean_accuracy", degrees_col="N total", null_mean_col="Null_mean", error_col="Binomial_error", tails="both", alpha=0.05)
improvements = data[data["Before_After"] == "Post-Treatment"]
print ("Individual patient improvement for patients:", ",".join(data["Patient"].astype(str).unique()), " on ", stimulus, "\n" + "="*150)
print (improvements.to_string())
print ("="*150)



