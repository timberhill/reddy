import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib

from datetime import datetime

class Plot(object):
    """
    A collection of Reddy plotters.
    """
    colour_index = 0

    @staticmethod
    def _month(unix_dt, year):
        # get a float month from usinx time and year
        d = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0: # simple leap year, good enough for reddit era
            d[1] = 29

        dt = datetime.fromtimestamp(unix_dt)
        return dt.month + float(dt.day) / d[dt.month-1]
    

    @staticmethod
    def _colour(accent=False):
        colours = ["#35424D", "#404D57", "#4B5761", "#687682", "#8495A3"]
        colour_accent = "#D1261D"#"#fc814a"
        if accent:
            return colour_accent
        else:
            i = Plot.colour_index
            Plot.colour_index = Plot.colour_index+1 if Plot.colour_index < len(colours)-1 else 0
            return colours[i]


    @staticmethod
    def timeseries_yearly(times, values, years, bin_where="post", accent=False):
        """
        Plot a number of posts/comments/upvotes as a function of time.

        times/values, array-like: a list of binned data (x/y). Can be a list of time series datas
        """
        if len(times) != len(values):
            raise ValueError(f"times [len={len(times)}] and values [len={len(values)}] must have the same length.")
        
        if isinstance(values[0], int) | isinstance(values[0], float): 
            # this is just one set of time series
            times  = [times,]
            values = [values,]
            years  = [years,]

        @ticker.FuncFormatter
        def _time_tick_formatter(x, pos):
            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            return month_names[int(x)][0:3]

        plt.style.use("../modules/reddy-timeseries.mplstyle")

        for i in range(len(times)):
            times_month = [Plot._month(t, years[i])-1 for t in times[i]]
            plt.step(times_month, values[i], 
                where=bin_where, 
                label=years[i],
                color=Plot._colour(accent),
                lw=4 if accent else 2,
                alpha=1 if accent else 0.5,
            )

        plt.xticks(range(0,12), rotation=-10, ha="left")
        plt.xlim(0, 12)
        plt.gca().xaxis.set_major_formatter(_time_tick_formatter)
        plt.legend()
