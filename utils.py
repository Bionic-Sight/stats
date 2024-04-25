import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy import stats
N_DECIMALS = 6



def df_binomial_error(df, col, n_col, eps=1e-6):
    df["Binomial_error"] = (df[col] * (1 - df[col]) / (df[n_col]) ** 0.5 + eps)
    return df

def mean_and_sem(diffs_df, col, verbose=False):
    mean_improvement = diffs_df[col].mean()
    std_improvement = diffs_df[col].std()
    sem_improvement = std_improvement / diffs_df.shape[0] ** 0.5
    n = diffs_df.shape[0]
    if verbose:
        print("%s Mean Improvement ± SEM: ", np.round(mean_improvement, N_DECIMALS), "±",
              np.round(sem_improvement, N_DECIMALS))
    return mean_improvement, std_improvement, sem_improvement, n

def z_test_df(df, mean_col, null_mean_col, error_col, tails="right", alpha=0.05):
    '''
    Z-score statistic: x-u / sigma
    :param df:
    :param mean_col:
    :param null_mean_col:
    :param error_col: standard deviation column
    :param tails: right, left or both
    :param alpha: significance level
    :return:
    '''
    df["z_stat"] = ((df[mean_col] - df[null_mean_col]) / df[error_col])
    if tails == "right_and_left" or tails == "both" or tails == "two-sided":
        df["p_value"] = 2 * (np.abs(df["z_stat"].apply(lambda x: 1 - norm.cdf(x))))
    elif tails == "right" or tails == "greater":
        df["p_value"] = np.abs(df["z_stat"].apply(lambda x: 1 - norm.cdf(x)))
    elif tails == "left" or tails == "less":
        df["p_value"] = np.abs(df["z_stat"].apply(lambda x: norm.cdf(x)))
    else:
        raise ValueError("tails must be 'right', 'left', or 'two-sided'")
    df["alpha"] = alpha
    df["significant"] = df["p_value"] < alpha
    return df

def t_test_df(df, mean_col, degrees_col, null_mean_col, error_col, tails="right", alpha=0.05):
    '''
    T-test statistic: x-u / (sigma / sqrt(n))
    :param df:
    :param mean_col:
    :param degrees_col: column with n, used for t-test CDF degrees of freedom
    :param null_mean_col: column with null hypothesis
    :param error_col: column with standard deviation (or other metric). Note I don't normalize by sqrt (n) here
    as convention because error col should already be normalized by n if using SEM
    :param tails:
    :param alpha:
    :return:

    '''
    df["t_stat"] = (df[mean_col] - df[null_mean_col]) / df[error_col]
    t_test_lambda = lambda df: stats.t.cdf(df["t_stat"], df=df[degrees_col])
    if tails == "right_and_left" or tails == "both" or tails == "two-sided":
        df["p_value"] = 2 * (1 - np.abs(df.apply(t_test_lambda, axis=1)))
    elif tails == "right" or tails == "greater":
        df["p_value"] =  np.abs(1 - df.apply(t_test_lambda, axis=1))
    elif tails == "left" or tails == "less":
        df["p_value"] =  np.abs(df.apply(t_test_lambda, axis=1))
    else:
        raise ValueError("tails must be 'right', 'left', or 'two-sided'")
    df["p_value"] = df["p_value"].astype(np.float32)
    df["alpha"] = alpha
    df["significant"] = df["p_value"] < alpha
    return df

def bump_to_chance(df, col, chance_value):
    df.loc[df[col] < chance_value,col] = chance_value
    return df

def t_test_numbers(sample_mean, null, error, df, tails="right", alpha=0.05):
    t_stat = (sample_mean - null) / error
    if tails == "right_and_left" or tails == "both" or tails == "two-sided":
        p_value = 2 * (1 - stats.t.cdf(t_stat, df=df))
    elif tails == "right" or tails == "greater":
        p_value = 1 - stats.t.cdf(t_stat, df=df)
    elif tails == "left" or tails == "less":
        p_value = stats.t.cdf(t_stat, df=df)
    else:
        raise ValueError("tails must be 'right', 'left', or 'two-sided'")
    return t_stat, p_value, p_value < alpha


SCIPY_ALTS = {
    "right": "greater",
    "left": "less",
    "both": "two-sided",
    "right_and_left": "two-sided"
}