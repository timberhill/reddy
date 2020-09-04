import numba
import numpy as np
from datetime import datetime, timedelta
from .utilities import time_to_unix


class TimeBin(object):
    """
    A collection of static Reddy binning functions.

    Uses numba package. Inspired by: https://stackoverflow.com/questions/45273731/binning-column-with-python-pandas
    """

    # TODO: implement median instead of mean (currently just dividing by N)

    # TODO: handle division by zero if upvote_ratio/binned_posts is 0 

    @staticmethod
    def _prepare_arguments(posts_data, binsize, start, end, step, utc):
        binsize = time_to_unix(binsize)
        start   = time_to_unix(start)
        end     = time_to_unix(end)
        
        # TODO:
        # maybe use centres for the bins 
        # OR
        # add an argument to choose that

        if step is not None: # running value (overlapping bins)
            step = time_to_unix(step)
            bins = np.arange(start, end, step)
        else: # proper non-overlapping bins
            bins = np.arange(start, end, binsize)
        
        if posts_data is None or len(posts_data) == 0:
            return [], bins, binsize
        
        created_data = posts_data["created_utc"].to_numpy() if utc else posts_data["created"].to_numpy()

        return created_data, bins, binsize


    @staticmethod
    def posts(posts_data, binsize, start, end, step=None, utc=False):
        """
        Bin posts data by numbers.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        start, datetime/int: bin size as a datetime object or unix time

        end,   datetime/int: bin size as a datetime object or unix time

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.
        
        utc, bool: [default=False] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        created_data, bins, binsize = TimeBin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        return TimeBin._posts_numba(created_data, bins, binsize)


    @staticmethod
    @numba.jit(nopython=True)
    def _posts_numba(xdata, bins, binsize):
        """
        See TimeBin.posts()
        """
        binned_data = [0]*len(bins)

        for x in xdata:
            for ibin in range(len(bins)):
                if (x >= bins[ibin]-binsize/2) and (x < bins[ibin]+binsize/2):
                    binned_data[ibin] += 1

        return bins, binned_data


    @staticmethod
    def comments(posts_data, binsize, start, end, step=None, utc=False, per_post=False):
        """
        Bin comment numbers.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        start, datetime/int: bin size as a datetime object or unix time

        end,   datetime/int: bin size as a datetime object or unix time

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.
        
        utc, bool: [default=False] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        created_data, bins, binsize = TimeBin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        comment_data = posts_data["num_comments"].to_numpy()
        return TimeBin._comments_numba(created_data, comment_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _comments_numba(created_data, comment_data, bins, binsize, per_post):
        """
        See TimeBin.comments()
        """
        binned_posts    = np.zeros(len(bins))
        binned_comments = np.zeros(len(bins))

        for i in range(len(created_data)):
            for ibin in range(len(bins)):
                if (created_data[i] >= bins[ibin]-binsize/2) and (created_data[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin]    += 1
                    binned_comments[ibin] += comment_data[i]

        if per_post:
            return bins, binned_comments / binned_posts
        else:
            return bins, binned_comments


    @staticmethod
    def score(posts_data, binsize, start, end, step=None, utc=False, per_post=False):
        """
        Bin score.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        start, datetime/int: bin size as a datetime object or unix time

        end,   datetime/int: bin size as a datetime object or unix time

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.
        
        utc, bool: [default=False] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        created_data, bins, binsize = TimeBin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()
        return TimeBin._score_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _score_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post):
        """
        See TimeBin.score()

        NOTE: Reddit API upvote_ratio = ups / (ups+downs)
        => Score = ups - downs = 2*ups - ups/upvote_ratio
        """
        binned_posts = np.zeros(len(bins))
        binned_score = np.zeros(len(bins))

        for i in range(len(created_data)):
            for ibin in range(len(bins)):
                if (created_data[i] >= bins[ibin]-binsize/2) and (created_data[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin] += 1
                    binned_score[ibin] += 2*ups_data[i] - ups_data[i]/upvote_ratio_data[i]

        if per_post:
            return bins, binned_score / binned_posts
        else:
            return bins, binned_score


    @staticmethod
    def interactions(posts_data, binsize, start, end, step=None, utc=False, per_post=False):
        """
        Bin the sum of upvotes and downvotes.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        start, datetime/int: bin size as a datetime object or unix time

        end,   datetime/int: bin size as a datetime object or unix time

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.
        
        utc, bool: [default=False] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        created_data, bins, binsize = TimeBin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()
        return TimeBin._interactions_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _interactions_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post):
        """
        See TimeBin.interactions()

        NOTE: Reddit API upvote_ratio = ups / (ups+downs)
        => Interactions = ups + downs = ups / upvote_ratio
        """
        binned_posts        = np.zeros(len(bins))
        binned_interactions = np.zeros(len(bins))

        for i in range(len(created_data)):
            for ibin in range(len(bins)):
                if (created_data[i] >= bins[ibin]-binsize/2) and (created_data[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin]        += 1
                    binned_interactions[ibin] += ups_data[i] / upvote_ratio_data[i]

        if per_post:
            return bins, binned_interactions / binned_posts
        else:
            return bins, binned_interactions



class TimeOfDayBin(object):

    @staticmethod
    def _prepare_arguments(posts_data, binsize=1.0, step=None, week=True, utc=True):
        if step is None:
            step = binsize

        binsize = time_to_unix(binsize)
        
        daily_bins = np.arange(0.0, 24.0, time_to_unix(step)/3600)
        weekly_bins = [daily_bins,] * 7 if week else [daily_bins,]

        if posts_data is None or len(posts_data) == 0:
            return np.array([]), weekly_bins, binsize
        
        def _unix_to_weekdays_hours(unix_t):
            dt = datetime.fromtimestamp(unix_t)
            return dt.weekday(), dt.hour + dt.minute/60 + dt.second/3600

        time_column = "created_utc" if utc else "created"
        time_data = np.array([_unix_to_weekdays_hours(t) for t in posts_data[time_column]])
        
        return time_data, weekly_bins, binsize


    @staticmethod
    def posts(posts_data, binsize=1.0, step=None, week=True, utc=True):
        """
        Bin posts data by numbers.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.

        week, bool: [default=True] calculate bins for every day of the week separately

        utc, bool: [default=True] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        time_data, bins, binsize = TimeOfDayBin._prepare_arguments(posts_data, binsize, step, week, utc)
        weekdays, hours = time_data.T
        binsize /= 3600 # convert to hours

        if week:
            for weekday in range(7):
                weekday_bins = bins[weekday]
                yield TimeOfDayBin._posts_numba(hours[weekdays == weekday], bins[weekday], binsize)
        else:
            return [ TimeOfDayBin._posts_numba(hours, bins[0], binsize), ]


    @staticmethod
    @numba.jit(nopython=True)
    def _posts_numba(xdata, bins, binsize):
        """
        See TimeOfDayBin.posts()
        """
        binned_data = np.zeros(len(bins))
        print(binsize)

        for x in xdata:
            for ibin in range(len(bins)):
                if (x >= bins[ibin]) and (x < bins[ibin]+binsize):
                    binned_data[ibin] += 1

        return bins, binned_data


    @staticmethod
    def score(posts_data, binsize=1.0, step=None, week=True, utc=True, per_post=True):
        """
        Bin posts data by score.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.

        week, bool: [default=True] calculate bins for every day of the week separately

        utc, bool: [default=True] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        time_data, bins, binsize = TimeOfDayBin._prepare_arguments(posts_data, binsize, step, week, utc)
        weekdays, hours = time_data.T
        binsize /= 3600 # convert to hours
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()

        if week:
            for weekday in range(7):
                weekday_bins = bins[weekday]
                yield TimeOfDayBin._score_numba(hours[weekdays == weekday], bins[weekday], binsize, ups_data, upvote_ratio_data, per_post)
        else:
            return [ TimeOfDayBin._score_numba(hours, bins[0], binsize, ups_data, upvote_ratio_data, per_post), ]


    @staticmethod
    @numba.jit(nopython=True)
    def _score_numba(xdata, bins, binsize, ups_data, upvote_ratio_data, per_post):
        """
        See TimeOfDayBin.score()
        """
        binned_posts = np.zeros(len(bins))
        binned_score = np.zeros(len(bins))

        for i in range(len(xdata)):
            for ibin in range(len(bins)):
                if (xdata[i] >= bins[ibin]-binsize/2) and (xdata[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin] += 1
                    binned_score[ibin] += 2*ups_data[i] - ups_data[i]/upvote_ratio_data[i]

        if per_post:
            return bins, binned_score / binned_posts
        else:
            return bins, binned_score


    @staticmethod
    def interactions(posts_data, binsize=1.0, step=None, week=True, utc=True, per_post=True):
        """
        Bin the sum of upvotes and downvotes.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.

        week, bool: [default=True] calculate bins for every day of the week separately

        utc, bool: [default=True] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        time_data, bins, binsize = TimeOfDayBin._prepare_arguments(posts_data, binsize, step, week, utc)
        weekdays, hours = time_data.T
        binsize /= 3600 # convert to hours
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()

        if week:
            for weekday in range(7):
                weekday_bins = bins[weekday]
                yield TimeOfDayBin._interactions_numba(hours[weekdays == weekday], bins[weekday], binsize, ups_data, upvote_ratio_data, per_post)
        else:
            return [ TimeOfDayBin._interactions_numba(hours, bins[0], binsize, ups_data, upvote_ratio_data, per_post), ]


    @staticmethod
    @numba.jit(nopython=True)
    def _interactions_numba(xdata, bins, binsize, ups_data, upvote_ratio_data, per_post):
        """
        See TimeOfDayBin.interactions()
        """
        binned_posts = np.zeros(len(bins))
        binned_interactions = np.zeros(len(bins))

        for i in range(len(xdata)):
            for ibin in range(len(bins)):
                if (xdata[i] >= bins[ibin]-binsize/2) and (xdata[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin]        += 1
                    binned_interactions[ibin] += ups_data[i] / upvote_ratio_data[i]

        if per_post:
            return bins, binned_interactions / binned_posts
        else:
            return bins, binned_interactions


    @staticmethod
    def comments(posts_data, binsize=1.0, step=None, week=True, utc=True, per_post=True):
        """
        Bin the comments.

        posts_data, DataFrame: Pandas dataframe containing posts

        binsize, timedelta/int: bin size as a timedelta object or unix time difference

        step, timedelta/int: [optional] distance between bins as a timedelta object or unix time difference. Equal to binsize by default.

        week, bool: [default=True] calculate bins for every day of the week separately

        utc, bool: [default=True] use UTC post time

        per_post, calculate values per post

        Returns:

            bin_centers, list/array: bin centers in unix time,

            values, list/array: number of posts in each bin
        """
        time_data, bins, binsize = TimeOfDayBin._prepare_arguments(posts_data, binsize, step, week, utc)
        weekdays, hours = time_data.T
        binsize /= 3600 # convert to hours
        comment_data = posts_data["num_comments"].to_numpy()

        if week:
            for weekday in range(7):
                weekday_bins = bins[weekday]
                yield TimeOfDayBin._comments_numba(hours[weekdays == weekday], bins[weekday], binsize, comment_data, per_post)
        else:
            return [ TimeOfDayBin._comments_numba(hours, bins[0], binsize, comment_data, per_post), ]


    @staticmethod
    @numba.jit(nopython=True)
    def _comments_numba(xdata, bins, binsize, comment_data, per_post):
        """
        See TimeOfDayBin.comments()
        """
        binned_posts = np.zeros(len(bins))
        binned_comments = np.zeros(len(bins))

        for i in range(len(xdata)):
            for ibin in range(len(bins)):
                if (xdata[i] >= bins[ibin]-binsize/2) and (xdata[i] < bins[ibin]+binsize/2):
                    binned_posts[ibin]    += 1
                    binned_comments[ibin] += comment_data[i]

        if per_post:
            return bins, binned_comments / binned_posts
        else:
            return bins, binned_comments
