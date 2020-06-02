import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .lockdown_start import load_national_lockdown_list

import matplotlib
font = {
    'family' : 'DejaVu Sans',
    'size'   : 9
}
matplotlib.rc('font', **font)


def plot_submission_frequency_histogram_2020(title, posts, upvote_limits=[0,], figsize=(12, 8), bins=np.arange(0, 180, 3)):
    colours = ["#092327", "#4F6D7A", "#9EA3B0"]
    alphas = [0.7, 0.7, 0.7]
    binsize = bins[1] - bins[0]

    year_start = datetime(2020, 1, 1, 0,0,0,0)
    getdays  = lambda t: (t-year_start).days + (t-year_start).seconds/(3600*24)

    posts["created_utc_obj"] = posts.apply(lambda row: datetime.utcfromtimestamp(row["created_utc"]), axis=1)
    days_all = [getdays(t) for t in posts["created_utc_obj"]]
    baseline = None

    f, ax = plt.subplots(1, 1, figsize=figsize)
    f.suptitle(title, ha="left", x=0.125, y=0.93)
    for i, ulim in enumerate(upvote_limits):
        days_some = [getdays(t) for t in posts.where(posts["ups"] > ulim).dropna(axis=0, how='all')["created_utc_obj"]]
        y, x = np.histogram(days_some, bins=bins)
        x = 0.5 * (x[1:] + x[:-1])

        if baseline is None:
            sample = y[(x >= 0) & (x <= 31)]
            baseline = np.mean(sample) if len(sample) > 0 else np.mean(y)

        y = 100 * y / baseline # normalize

        if y[0] != 0:
            x = np.insert(x, 0, bins[0]-binsize)
            y = np.insert(y, 0, 0)
        if y[-1] != 0:
            x = np.insert(y, -1, bins[-1]+binsize)
            y = np.insert(y, -1, 0)

        lw = 3 if i == 0 else 1
        ls = "-" if i == 0 else "-"

        ax.step(x, y, where="mid", c=colours[i], alpha=alphas[i], lw=lw, ls=ls, label=f"upvotes > {ulim}")

    ax.set_xticks([0, 15, 31, 46, 60, 75, 91, 106, 121, 136, 152])
    ax.set_xticklabels(["Jan 1", "15", "Feb 1", "15", "Mar 1", "15", "Apr 1", "15", "May 1", "15", "June 1"])

    ax.set_ylim(0, ax.get_ylim()[1])
    ax.set_xlim(min(days_all), max(days_all)+bins[2]-bins[0])

    # plot lockdown dates
    def plot_vline(ax, date, label="", color="#f17b77", yoffset=0.5, fontsize=12, alpha=1):
        date_days = getdays(date)
        line = ax.axvline(date_days, c=color, alpha=alpha, zorder=-1)
        # ax.text(date_days+0.7, ax.get_ylim()[1]-yoffset, label, color=color, va="top", fontsize=fontsize, alpha=alpha)
        return ax, line
    
    lockdown_dates = load_national_lockdown_list()
    for i, row in lockdown_dates.iterrows():
        ax, line = plot_vline(ax, row["Start"].to_pydatetime(), alpha=0.5)
    
    # plot baseline
    ax.axhline(100, color="k", ls="--", lw=1, alpha=0.6)

    # labels = ["New York", "United Kingdom", "Australia"]
    # labeled_dates = lockdown_dates.where(lockdown_dates["State"].isin(labels)).dropna(axis=0, how='any')
    # print(labeled_dates)
    # yoffset = 0.15
    # for i, row in labeled_dates.iterrows():
    #     ax, line = plot_vline(ax, row["Start"].to_pydatetime(), row["State"], color="#A93F55", alpha=1, yoffset=yoffset)
    #     yoffset += 2

    ax.set_xlabel("Date")
    ax.set_ylabel("Number of submissions relative to the first week of 2020")

    ax.set_xlim(0, getdays(datetime.utcnow()) - 7)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(line)
    labels.append("National lockdown dates")
    ax.legend(handles, labels, frameon=False)

    return f, ax


def plot_submission_time_histogram(title, posts, figsize=(12, 8), 
        bins=np.arange(0, 24, 1), 
        metric="number", 
        main_range=(datetime(2020,4,1,0,0,0), datetime.utcnow()), 
        reference_range=(datetime(2020,1,1,0,0,0), datetime(2020,2,1,0,0,0)),
        success_score=100):

    colours = ["#A71D31", "#40434E", "#9EA3B0"]
    alphas = [1, 1, 0.7]

    def post_decimal_hour_utc(post):
        d = datetime.fromtimestamp(post.created_utc)
        return d.hour + d.minute/60 + d.second/3600
    
    posts["decimal_hour_utc"] = posts.apply(post_decimal_hour_utc, axis=1)
    posts["int_hour_utc"] = posts.apply(lambda post: datetime.fromtimestamp(post.created_utc).hour, axis=1)

    main_posts = posts.where(
            (posts.created_utc > main_range[0].timestamp()) & 
            (posts.created_utc < main_range[1].timestamp())
        ).dropna(how="all")

    reference_posts = posts.where(
            (posts.created_utc > reference_range[0].timestamp()) & 
            (posts.created_utc < reference_range[1].timestamp())
        ).dropna(how="all")
        
    hours = np.arange(0, 24, 1)
    main_y = np.zeros_like(hours)
    reference_y = np.zeros_like(hours)
    for i, h in enumerate(hours):
        main_slice = main_posts.where(posts.int_hour_utc == h).dropna(how="all")
        reference_slice = reference_posts.where(posts.int_hour_utc == h).dropna(how="all")
        
        main_y[i]      = 100 * len(main_slice.where(main_slice.ups > 100).dropna(how="all").index) / len(main_slice.index)
        reference_y[i] = 100 * len(reference_slice.where(reference_slice.ups > 100).dropna(how="all").index) / len(reference_slice.index)

    # to handle step plot edges
    hours = np.append(hours, 24)
    main_y = np.append(main_y, main_y[-1])
    reference_y = np.append(reference_y, reference_y[-1])

    f, ax = plt.subplots(1, 1, figsize=figsize)
    f.suptitle(title, ha="left", x=0.125, y=0.93)

    ax.step(hours, main_y, where="post", c=colours[0], alpha=alphas[0], lw=3, ls="-", label=f"lockdown")
    ax.step(hours, reference_y, where="post", c=colours[1], alpha=alphas[1], lw=2, ls=":", label=f"before")

    ax.set_xticks(np.arange(0, 26, 2))

    ax.set_xlabel("Submission time")
    ax.set_ylabel("Score")

    ax.set_xlim(0, 24)
    ax.legend()

    return f, ax