import utils
from groupings import *
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel

patients_excluded = [114]
alternative = "two-sided"
dose_group = "all" # "1", "2", "3", "4", or "all"
patient_group = "all" # "low-vision", "tunnel-vision", or "all"

data = pd.read_excel("maze_stats.xlsx")

