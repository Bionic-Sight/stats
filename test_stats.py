import unittest
import utils
import numpy as np
import scipy
np.random.seed(42)

class TestStats(unittest.TestCase):
    def test_pairwise_t(self):
        '''
        TODO: Why isn't this working?
        :return:
        '''
        data1 = np.abs(np.random.normal(0, 1, 100))
        data2 = np.abs(np.random.normal(0, 1, 100))
        diff = data2 - data1
        mean_improvement = np.mean(diff)
        sem_improvement = np.std(diff) / np.sqrt(len(diff))
        n = data1.shape[0]

        t, p, sig = utils.t_test_numbers(mean_improvement,
                                         null=0,
                                         error=sem_improvement,
                                         df=n - 1,
                                         tails="both",
                                   alpha=0.05)
        t_stat, p_val = scipy.stats.ttest_rel(data1, data2, alternative="two-sided")
        t_stat2, p_val2 = scipy.stats.ttest_rel([0] * n, diff, alternative="two-sided")
        print (t, t_stat)
        # Proof that the t-stat is same whether you calculate timepoint diffs against 0 or input each timepoint separately
        assert np.allclose(t_stat2, t_stat, atol=1e-5)
        # Proof that the custom implementation is correct by comparing to scipy
        assert np.allclose(t, t_stat2, atol=1e-5)



if __name__ == '__main__':
    unittest.main()