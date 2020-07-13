import numba
import numpy as np
from datetime import datetime, timedelta


class Bin(object):
    """
    A collection of static Reddy binning functions.

    Uses numba package. Inspired by: https://stackoverflow.com/questions/45273731/binning-column-with-python-pandas
    """

    # TODO: implement median instead of mean (currently just dividing by N)

    @staticmethod
    def _prepare_arguments(posts_data, binsize, start, end, step, utc):
        def _handle_time(value):
            """
            Returns unix time or time difference in seconds.
            """
            if isinstance(value, datetime):
                return value.timestamp()
            elif isinstance(value, timedelta):
                return value.total_seconds()
            elif type(value) is float or type(value) is int:
                return value
            else:
                print(type(value), isinstance(value, datetime), value)
                raise ValueError(f"Invalid time format/value encountered: {value}.")
        
        binsize = _handle_time(binsize)
        start   = _handle_time(start)
        end     = _handle_time(end)
        
        # TODO:
        # maybe use centres for the bins 
        # OR
        # add an argument to choose that

        if step is not None: # running value (overlapping bins)
            step = _handle_time(step)
            bins = np.arange(start, end+step, step)
        else: # proper non-overlapping bins
            bins = np.arange(start, end+binsize, binsize)
        
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
        created_data, bins, binsize = Bin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        return Bin._posts_numba(created_data, bins, binsize)


    @staticmethod
    @numba.jit(nopython=True)
    def _posts_numba(xdata, bins, binsize):
        """
        See Bin.posts()
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
        created_data, bins, binsize = Bin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        comment_data = posts_data["num_comments"].to_numpy()
        return Bin._comments_numba(created_data, comment_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _comments_numba(created_data, comment_data, bins, binsize, per_post):
        """
        See Bin.comments()
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
        created_data, bins, binsize = Bin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()
        return Bin._score_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _score_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post):
        """
        See Bin.score()

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
        created_data, bins, binsize = Bin._prepare_arguments(posts_data, binsize, start, end, step, utc)
        ups_data = posts_data["ups"].to_numpy()
        upvote_ratio_data = posts_data["upvote_ratio"].to_numpy()
        return Bin._interactions_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post)


    @staticmethod
    @numba.jit(nopython=True)
    def _interactions_numba(created_data, ups_data, upvote_ratio_data, bins, binsize, per_post):
        """
        See Bin.interactions()

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
