import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .lockdown_start import load_national_lockdown_list

import matplotlib
font = {
    'family' : 'DejaVu Sans',
    'size'   : 16
}
matplotlib.rc('font', **font)


def plot_submission_frequency_histogram_2020(title, posts, upvote_limits=[0,], figsize=(12, 8), bins=np.arange(0, 180, 3)):
    colours = ["#64a587", "#446b50", "#010101"]
    alphas = [1, 0.6, 0.6]
    binsize = bins[1] - bins[0]

    year_start = datetime(2020, 1, 1, 0,0,0,0)
    getdays  = lambda t: (t-year_start).days + (t-year_start).seconds/(3600*24)

    posts["created_utc_obj"] = posts.apply(lambda row: datetime.utcfromtimestamp(row["created_utc"]), axis=1)
    days_all = [getdays(t) for t in posts["created_utc_obj"]]

    f, ax = plt.subplots(1, 1, figsize=(12, 8))
    f.suptitle(title, ha="left", x=0.125, y=0.93)
    for i, ulim in enumerate(upvote_limits):
        days_some = [getdays(t) for t in posts.where(posts["ups"] > ulim).dropna(axis=0, how='any')["created_utc_obj"]]
        y, x = np.histogram(days_some, bins=bins)
        x = 0.5 * (x[1:] + x[:-1])
        # handle edges
        if y[0] != 0:
            x = np.insert(x, 0, bins[0]-binsize)
            y = np.insert(y, 0, 0)
        if y[-1] != 0:
            x = np.insert(y, -1, bins[-1]+binsize)
            y = np.insert(y, -1, 0)

        ax.fill(x, y, c=colours[i], alpha=alphas[i], lw=0, label=f"upvotes > {ulim}")

    ax.set_xticks([0, 15, 31, 46, 60, 75, 91, 106, 121, 136, 152])
    ax.set_xticklabels(["Jan 1", "15", "Feb 1", "15", "Mar 1", "15", "Apr 1", "15", "May 1", "15", "June 1"])

    ax.set_ylim(0, ax.get_ylim()[1])
    ax.set_xlim(min(days_all), max(days_all)+bins[2]-bins[0])

    # plot lockdown dates
    def plot_vline(ax, date, label="", color="#f17b77", yoffset=0.5, fontsize=12, alpha=1):
        date_days = getdays(date)
        line = ax.axvline(date_days, c=color, alpha=alpha, zorder=-1)
        ax.text(date_days+0.7, ax.get_ylim()[1]-yoffset, label, color=color, va="top", 
            fontsize=fontsize, alpha=alpha)
        return ax, line
    
    lockdown_dates = load_national_lockdown_list()
    for i, row in lockdown_dates.iterrows():
        ax, line = plot_vline(ax, row["Start"].to_pydatetime(), alpha=0.5)

    # labels = ["New York", "United Kingdom", "Australia"]
    # labeled_dates = lockdown_dates.where(lockdown_dates["State"].isin(labels)).dropna(axis=0, how='any')
    # print(labeled_dates)
    # yoffset = 0.15
    # for i, row in labeled_dates.iterrows():
    #     ax, line = plot_vline(ax, row["Start"].to_pydatetime(), row["State"], color="#A93F55", alpha=1, yoffset=yoffset)
    #     yoffset += 2

    ax.set_xlabel("Date")
    ax.set_ylabel("N")

    ax.set_xlim(0, getdays(datetime.utcnow()))

    handles, labels = ax.get_legend_handles_labels()
    handles.append(line)
    labels.append("National lockdown dates")
    ax.legend(handles, labels, frameon=False)

    return f, ax