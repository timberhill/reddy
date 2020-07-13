import numpy as np
import matplotlib.pyplot as plt

import matplotlib
font = {
    'family' : 'DejaVu Sans',
    'size'   : 16
}
matplotlib.rc('font', **font)

class Plot(object):
    """
    A collection of Reddy plotters.
    """

    @staticmethod
    def numbers(binned_data, reference_data=None):
        """
        Plot a number of posts/comments/upvotes, optionally divided by the "reference_data"
        """
        plt.step(binned_data[0][0:-1], binned_data[1], where="post")
        plt.show()
