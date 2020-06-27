import os
import sys

from sqlalchemy import create_engine, Column, ForeignKey, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
Base = declarative_base()

from collections.abc import Iterable
from .containers import RedditPost


class DataContext(object):
    def __init__(self, path=None, profiler=False):
        if path is None:
            from .config import Config
            path = Config().db_path

        self.path = path
        self.engine = create_engine(f"sqlite:///{path}", echo=profiler)
        Base.metadata.bind = self.engine

        self.create_database_structure()

        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        self.session.close()
    
    def rollback(self):
        self.session.rollback()


    def create_database_structure(self):
        """
        Create database structure if it doesn't exist.
        """
        Base.metadata.create_all(self.engine)
    

    def commit(self):
        """
        Commit the changes to the database.
        """
        self.session.commit()


    def add_subreddit(self, name, raise_existing=False):
        """
        Add subreddit entry to the database.

        name, str: name of the subreddit,

        raise_existing, bool: raise if the subreddit name exists

        Returns: Subreddit object - existing or created.
        """
        name = name.lower()

        # check if subreddit exists
        existing = self.session.query(Subreddit).filter(Subreddit.name == name).first()
        if existing is not None:
            if raise_existing:
                raise ValueError(f"Subreddit {name} is already in the database. Set raise_existing=False in DataContext.add_subreddit() to ignore this error in the future.")
            else:
                return existing

        # create subreddit entry
        entry = Subreddit()
        entry.name = name
        self.session.add(entry)

        return entry


    def add_posts(self, posts, update=True):
        """
        Add a RedditPost or a list of posts to the database. Subreddit entries are added automatically.

        posts, array/RedditPost: single post object ot a list of post objects. Added in bulk.

        update, bool: update the entry if the post id already exists in the database
        """

        if not isinstance(posts, Iterable):
            posts = [posts,]
        
        subreddit_names = set([post.subreddit for post in posts])

        for subreddit_name in subreddit_names:
            subreddit = self.add_subreddit(name=subreddit_name, raise_existing=False)
            subreddit_posts = [post for post in posts if post.subreddit == subreddit_name]

            for post in subreddit_posts:
                existing = self.session.query(Post).filter(Post.post_id == post.id).first()

                if existing is None:
                    entry = self._post_model_to_entry(post)
                    entry.subreddit = subreddit
                    self.session.add(entry)
                else:
                    existing = self._update_post_entry(existing, post)


    def select_posts(self, subreddit_name=None, daterange=None, utc=True, include_removed=True):
        """
        Select and filter posts.
        """
        subreddit_name = subreddit_name.lower()
        
        query = self.session.query(Post)
        if subreddit_name is not None:
            query = query.filter(Post.subreddit.has(name=subreddit_name))
        if daterange is not None:
            if utc:
                if daterange[0] is not None:
                    query = query.filter(Post.created_utc >= daterange[0])
                if daterange[1] is not None:
                    query = query.filter(Post.created_utc <= daterange[1])
            else:
                if daterange[0] is not None:
                    query = query.filter(Post.created >= daterange[0])
                if daterange[1] is not None:
                    query = query.filter(Post.created <= daterange[1])
        if not include_removed:
            query = query.filter(Post.removed == False)
        
        query = query.order_by(Post.created_utc)

        return [self._post_entry_to_model(entry) for entry in query.all()]


    def _update_post_entry(self, target, source):
        """
        Updated target<Post> with values from source<Post>.
        """
        target.post_id         = target.post_id if source.id==source.id else source.id
        # target.author          = target.author if source.author==source.author else source.author
        target.author_premium  = target.author_premium if source.author_premium==source.author_premium else source.author_premium
        target.subreddit_subscribers = target.subreddit_subscribers if source.subreddit_subscribers==source.subreddit_subscribers else source.subreddit_subscribers
        target.title           = target.title if source.title==source.title else source.title
        target.downs           = target.downs if source.downs==source.downs else source.downs
        target.ups             = target.ups if source.ups==source.ups else source.ups
        target.upvote_ratio    = target.upvote_ratio if source.upvote_ratio==source.upvote_ratio else source.upvote_ratio
        target.score           = target.score if source.score==source.score else source.score
        target.selftext        = target.selftext if source.selftext==source.selftext else source.selftext
        target.removed         = target.removed if source.removed==source.removed else source.removed
        target.num_comments    = target.num_comments if source.num_comments==source.num_comments else source.num_comments
        target.total_awards_received = target.total_awards_received if source.total_awards_received==source.total_awards_received else source.total_awards_received
        # target.permalink       = target.permalink if source.permalink==source.permalink else source.permalink
        # target.url             = target.url if source.url==source.url else source.url
        # target.created         = target.created if source.created==source.created else source.created
        # target.created_utc     = target.created_utc if source.created_utc==source.created_utc else source.created_utc

        return target


    def _post_model_to_entry(self, redditpost):
        """
        Assign values of RedditPost to Post entry.
        """
        entry = Post()
        entry.post_id         = redditpost.id
        entry.author          = redditpost.author
        entry.author_premium  = redditpost.author_premium
        entry.subreddit_subscribers = redditpost.subreddit_subscribers
        entry.title           = redditpost.title
        entry.downs           = redditpost.downs
        entry.ups             = redditpost.ups
        entry.upvote_ratio    = redditpost.upvote_ratio
        entry.score           = redditpost.score
        entry.selftext        = redditpost.selftext
        entry.removed         = redditpost.removed
        entry.num_comments    = redditpost.num_comments
        entry.total_awards_received = redditpost.total_awards_received
        entry.permalink       = redditpost.permalink
        entry.url             = redditpost.url
        entry.created         = redditpost.created
        entry.created_utc     = redditpost.created_utc

        return entry


    def _post_entry_to_model(self, entry):
        """
        Assign values of Post entry to RedditPost.
        """
        return RedditPost({
            "id"             : entry.post_id,
            "subreddit"      : entry.subreddit.name,
            "author"         : entry.author,
            "author_premium" : entry.author_premium,
            "subreddit_subscribers" : entry.subreddit_subscribers,
            "title"          : entry.title,
            "downs"          : entry.downs,
            "ups"            : entry.ups,
            "upvote_ratio"   : entry.upvote_ratio,
            "score"          : entry.score,
            "selftext"       : entry.selftext,
            "removed"        : entry.removed,
            "num_comments"   : entry.num_comments,
            "total_awards_received" : entry.total_awards_received,
            "permalink"      : entry.permalink,
            "url"            : entry.url,
            "created"        : entry.created,
            "created_utc"    : entry.created_utc,
        })


class Subreddit(Base):
    __tablename__ = 'subreddits'

    id   = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
 
 
class Post(Base):
    __tablename__ = 'posts'
    
    id             = Column(Integer, primary_key=True)

    subreddit_id   = Column(Integer, ForeignKey('subreddits.id'))
    subreddit      = relationship(Subreddit)

    post_id        = Column(String(10), nullable=False, unique=True)
    author         = Column(String(100))
    author_premium = Column(Boolean, default=False)
    subreddit_subscribers = Column(Integer)
    title          = Column(String(250))
    downs          = Column(Integer)
    ups            = Column(Integer)
    upvote_ratio   = Column(Float)
    score          = Column(Integer)
    selftext       = Column(String(1000))
    removed        = Column(Boolean, default=False)
    num_comments   = Column(Integer)
    total_awards_received = Column(Integer)
    permalink      = Column(String(250))
    url            = Column(String(250))
    created        = Column(Integer)
    created_utc    = Column(Integer)
