import utils
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel


stimulus = "Direction"
alternative = "two-sided"
patients_excluded = [114]


data = pd.read_excel("MDLO.xlsx", sheet_name=stimulus)
data["Before_After"] = data["Visit"].apply(lambda x: "Baseline" if x == "Baseline" else "Post-Treatment")
data = data[~data["Patient"].isin(patients_excluded)]
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

data = utils.df_binomial_error(data, "Mean_accuracy", "N total")
# Use the baseline mean accuracy as the null hypothesis
diffs = data[data["Before_After"] == "Baseline"].merge(data[data["Before_After"] == "Post-Treatment"], on="Patient",
                                                        suffixes=("_before", "_after"),
                                                        how="outer")
diffs["Improvement on %s"%stimulus] = diffs["Mean_accuracy_after"] - diffs["Mean_accuracy_before"]
diffs = diffs[["Patient", "Improvement on %s"%stimulus]].fillna(0)
mean_improvement, std_improvement, sem_improvement, _ = utils.mean_and_sem(diffs, "Improvement on %s"%stimulus, verbose=True)
print ("Paired %s sample improvement in (n=%d patients) on "%(alternative, diffs.shape[0]), stimulus, "\n" + "="*150)
print (diffs.to_string())
print (ttest_rel([0] * diffs.shape[0], diffs["Improvement on %s"%stimulus].values, alternative=alternative), "\n" + "="*150)


improvements = data[data["Before_After"] == "Post-Treatment"]
print ("Individual patient improvement for patients:", ",".join(data["Patient"].astype(str).unique()), " on ", stimulus, "\n" + "="*150)
print (improvements.to_string())
print ("="*150)



