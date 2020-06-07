import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .lockdown_start import load_national_lockdown_list

import matplotlib
font = {
    'family' : 'DejaVu Sans',
    'size'   : 16
}
matplotlib.rc('font', **font)


def plot_submission_frequency_histogram_2020(title, posts, upvote_limits=[0,], figsize=(12, 8), bins=np.arange(0, 180, 7)):
    colours = ["#092327", "#4F6D7A", "#9EA3B0"]
    alphas = [0.7, 0.7, 0.7]
    binsize = bins[1] - bins[0]

    year_start = datetime(2020, 1, 1, 0,0,0,0)
    getdays  = lambda t: (t-year_start).days + (t-year_start).seconds/(3600*24)

    days_all = [getdays(post.created_utc_datetime) for post in posts]
    baseline = None

    f, ax = plt.subplots(1, 1, figsize=figsize)
    f.suptitle(title, ha="left", x=0.125, y=0.93)
    for i, ulim in enumerate(upvote_limits):
        days_some = [getdays(post.created_utc_datetime) for post in posts if post.ups > ulim]
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
    for t in lockdown_dates["Start"]:
        ax, line = plot_vline(ax, t, alpha=0.5)
    
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
    ax.set_ylabel("Number of submissions relative to January 2020")

    ax.set_xlim(0, getdays(datetime.utcnow())-binsize)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(line)
    labels.append("National lockdown dates")
    ax.legend(handles, labels, frameon=False)

    return f, ax


def plot_submission_time_histogram(title, posts, figsize=(12, 8),
        metric="number", 
        main_range=(datetime(2020,4,1,0,0,0), datetime(2020,5,1,0,0,0)), 
        reference_range=(datetime(2020,1,1,0,0,0), datetime(2020,2,1,0,0,0)),
        success_score=100,
        utc=False,
        average_method="mean"):
    """
    Plot a metric as a function of time of day (1 hour bins)

    metric, str: Y axis metric, one of:
                 posts - number of posts submitted (default)
                 comments - number of comments in all posts
                 upvotes - number of all upvotes
                 success - fraction of 'successful' posts (upvotes > success_score)

    main_range, tuple: main data date range (red line)

    reference_range, tuple: reference data date range (dotted line)
    
    success_score, int: upvote threshold for a post to be considered successful
    """
    if average_method == "mean":
        average_method = np.mean
    elif average_method == "median":
        average_method = np.median

    colours = ["#A71D31", "#40434E", "#9EA3B0"]
    alphas = [1, 1, 0.7]

    main_posts = [
        post for post in posts 
        if (post.created_utc > main_range[0].timestamp()) & 
           (post.created_utc < main_range[1].timestamp())
    ]
    reference_posts = [
        post for post in posts 
        if (post.created_utc > reference_range[0].timestamp()) & 
           (post.created_utc < reference_range[1].timestamp())
    ]

    hours = np.arange(0, 24, 1)
    main_y      = np.zeros_like(hours, dtype=np.float)
    reference_y = np.zeros_like(hours, dtype=np.float)
    for i, h in enumerate(hours):
        get_hour = lambda post: post.created_utc_datetime.hour if utc else post.created_datetime.hour
        main_slice      = [post for post in main_posts      if get_hour(post) == h]
        reference_slice = [post for post in reference_posts if get_hour(post) == h]
        
        if metric == "posts":
            ylabel = "Number of posts"
            main_y[i]      = len(main_slice)
            reference_y[i] = len(reference_slice)

        elif metric == "comments":
            ylabel = "Comments per post"
            main_y[i]      = average_method([post.num_comments for post in main_slice])
            reference_y[i] = average_method([post.num_comments for post in reference_slice])

        elif metric == "upvotes":
            ylabel = "Upvotes per post"
            main_y[i]      = average_method([post.ups for post in main_slice])
            reference_y[i] = average_method([post.ups for post in reference_slice])

        elif metric == "success":
            ylabel = f"Percentge of posts with upvotes > {success_score}"
            main_y[i]      = np.sum([1.0 for post in main_slice      if post.ups > success_score]) / len(main_slice)
            reference_y[i] = np.sum([1.0 for post in reference_slice if post.ups > success_score]) / len(reference_slice)

        else:
            raise ValueError("Unexpected value encountered for 'metric' argument in plotters.plot_submission_time_histogram()")

    # to handle step plot edges
    hours = np.append(hours, 24)
    main_y = np.append(main_y, main_y[-1])
    reference_y = np.append(reference_y, reference_y[-1])

    f, ax = plt.subplots(1, 1, figsize=figsize)
    f.suptitle(title, ha="left", x=0.125, y=0.93)

    ax.step(hours, main_y, where="post", c=colours[0], alpha=alphas[0], lw=3, ls="-", label=f"lockdown")
    ax.step(hours, reference_y, where="post", c=colours[1], alpha=alphas[1], lw=2, ls=":", label=f"before")

    ax.set_xticks(np.arange(0, 26, 2))

    timezone = "UTC" if utc else "Local"
    ax.set_xlabel(f"Submission time ({timezone})")
    ax.set_ylabel(ylabel)

    ax.set_xlim(0, 24)
    ax.legend()

    return f, ax