import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy import stats

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
    if tails == "right_and_left" or tails == "both" or tails == "two":
        df["p_value"] = 2 * (np.abs(df["z_stat"].apply(lambda x: 1 - norm.cdf(x))))
    elif tails == "right" or tails == "greater":
        df["p_value"] = np.abs(df["z_stat"].apply(lambda x: 1 - norm.cdf(x)))
    elif tails == "left" or tails == "less":
        df["p_value"] = np.abs(df["z_stat"].apply(lambda x: norm.cdf(x)))
    else:
        raise ValueError("tails must be 'right', 'left', or 'both'")
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
    if tails == "right_and_left" or tails == "both" or tails == "two":
        df["p_value"] = 2 * np.abs(df.apply(t_test_lambda, axis=1))
    elif tails == "right" or tails == "greater":
        df["p_value"] =  np.abs(1 - df.apply(t_test_lambda, axis=1))
    elif tails == "left" or tails == "less":
        df["p_value"] =  np.abs(df.apply(t_test_lambda, axis=1))
    else:
        raise ValueError("tails must be 'right', 'left', or 'both'")
    df["p_value"] = df["p_value"].astype(np.float32)
    df["alpha"] = alpha
    df["significant"] = df["p_value"] < alpha
    return df


def t_test_numbers(sample_mean, null, error, df, tails="right", alpha=0.05):
    t_stat = (sample_mean - null) / error
    if tails == "right_and_left" or tails == "both" or tails == "two":
        p_value = 2 * (1 - stats.t.cdf(t_stat, df=df))
    elif tails == "right" or tails == "greater":
        p_value = 1 - stats.t.cdf(t_stat, df=df)
    elif tails == "left" or tails == "less":
        p_value = stats.t.cdf(t_stat, df=df)
    else:
        raise ValueError("tails must be 'right', 'left', or 'both'")
    return t_stat, p_value, p_value < alpha