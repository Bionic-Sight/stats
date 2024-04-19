import utils
import pandas as pd
from scipy.stats import ttest_rel


stimulus = "Objects"
data = pd.read_excel("MDLO.xlsx", sheet_name=stimulus)
data["Before_After"] = data["Visit"].apply(lambda x: "Baseline" if x == "Baseline" else "Post-Treatment")
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

data["Binomial_error"] = (data["Mean_accuracy"] * (1 - data["Mean_accuracy"]) / data["N total"]) ** 0.5

# Use the baseline mean accuracy as the null hypothesis
data = utils.t_test_df(data, "Mean_accuracy", null_mean_col="Null_mean", degrees_col="N total", error_col="Binomial_error", tails="right", alpha=0.05)
diffs = data[data["Before_After"] == "Baseline"].merge(data[data["Before_After"] == "Post-Treatment"], on="Patient",
                                                        suffixes=("_before", "_after"),
                                                        how="outer")
diffs["Improvement"] = diffs["Mean_accuracy_after"] - diffs["Mean_accuracy_before"]
diffs = diffs[["Patient", "Improvement"]].fillna(0)
print ("Paired sample improvement in (n=%d patients) on "%diffs.shape[0], stimulus, "\n" + "="*150)
print (ttest_rel([0] * diffs.shape[0], diffs["Improvement"].values, alternative="two-sided"), "\n" + "="*150)


improvements = data[data["Before_After"] == "Post-Treatment"]
print ("Individual patient improvement for patients:", ",".join(data["Patient"].astype(str).unique()), " on ", stimulus, "\n" + "="*150)
print (improvements.to_string())
print ("="*150)


#print (ttest_rel(data[data["Before_After"] == "Baseline"]["Mean_accuracy"].values, data[data["Before_After"] == "Post-Treatment"]["Mean_accuracy"].values, alternative="two-sided"))



