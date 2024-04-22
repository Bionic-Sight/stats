import utils
from groupings import *
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel

patients_excluded = [114]
alternative = "two-sided"
dose_group = "all" # "1", "2", "3", "4", or "all"
patient_group = "tunnel-vision" # "low-vision", "tunnel-vision", or "all"

# Load and preprocess data
group_data = pd.read_excel("logMAR.xlsx", sheet_name="data")
group_data = group_data[~group_data["Patient"].isin(patients_excluded)]
group_data["Patient_group"] = group_data["Patient"].map(HIGH_DOSE_PATIENT_GROUPS)
group_data["Dose_group"] = group_data["Patient"].map(DOSE_GROUPS)
if dose_group != "all":
    group_data = group_data[group_data["Dose_group"] == dose_group]
if patient_group != "all":
    group_data = group_data[group_data["Patient_group"] == patient_group]


'''
Note that acuity "improvement" is a negative logMAR change, so either use a negative mean with a left-tailed test or a
an absolute mean with a right-tailed test.
'''
mean_improvement, std_improvement, sem_improvement, n = utils.mean_and_sem(group_data,  "logMAR Improvement, 50% Threshold", verbose=False)


'''
Paired-t test for the mean improvement in logMAR acuity using a 50% threshold.
You can calculate the differences yourself or feed the original data to the ttest_rel function- it doesn't 
matter because it's either a (diff - 0) = diff or (after - before) = diff.
'''

print ("logMAR Mean Improvement ± SEM:", np.round(mean_improvement, 4), "±", np.round(sem_improvement, 4))
print ("Paired sample improvement in (n=%d patients) on acuity "%n, "\n" + "="*150)
print (ttest_rel(group_data["Baseline logMAR, 50% Threshold"].values, group_data["After logMAR, 50% Threshold"].values, alternative="two-sided"))


'''
Individual one sample t-tests comparing the 50% threshold acuity to a null hypothesis of chance at baseline for a 
before-after significance test on each patient
'''
individual_data = pd.read_excel("logMAR.xlsx", sheet_name="individual_50")
individual_data["Patient_group"] = individual_data["Patient"].map(HIGH_DOSE_PATIENT_GROUPS)
individual_data["Dose_group"] = individual_data["Patient"].map(DOSE_GROUPS)
if dose_group != "all":
    individual_data = individual_data[individual_data["Dose_group"] == dose_group]
if patient_group != "all":
    individual_data = individual_data[individual_data["Patient_group"] == patient_group]

individual_data["Mean_accuracy"] = individual_data["N correct"] / individual_data["N total"]
individual_data["Binomial_error"] = (individual_data["Mean_accuracy"] * (1 - individual_data["Mean_accuracy"]) / individual_data["N total"]) ** 0.5
individual_data["Null_mean"] = 0.25
individual_improvements = utils.t_test_df(individual_data, "Mean_accuracy", degrees_col="N total",null_mean_col="Null_mean", error_col="Binomial_error", tails=alternative, alpha=0.05)
individual_improvements = individual_improvements[individual_improvements["Before_After"] == "Post-Treatment"]
print ("\n" + "="*150)
print ("Individual patient improvement for patients:", ",".join(individual_improvements["Patient"].astype(str).unique()), " on acuity", "\n" + "="*150)
print (individual_improvements.to_string())