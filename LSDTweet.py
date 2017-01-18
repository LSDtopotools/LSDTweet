# -*- coding: utf-8 -*-
"""
Script that scrapes commit info from a git repo logs, formats the info into
a tweet and then tweets it.

Only works on Python 3.4 and requires Tweepy, GitPython and a secrets.py
file to handle the twitter api keys. It is assumed that the machine this script
is run on has github authentication configured.

Call at the terminal with the path to the repo to tweet from or put it in your
crontab.

SWDG 18/1/17
"""
import tweepy
import git
import sys
from secrets import *


def ScrapeGIT(repoURL):
    """
    Given a path to a local git repo, return the commit message and hash.
    """
    g = git.cmd.Git('/home/sgrieve/LSDDev/')
    g.pull()
    Message = (g.log('-1', '--pretty=format:%s'))
    Hash = (g.log('-1', '--pretty=format:%h'))

    return Hash, Message


def check_length_for_tweet(Hash, Message):
    """
    Recursively remove a word from the message until it is small enough to tweet
    """
    if len(Hash) + len(Message) > 140:
        # get rid of a word
        message = ' '.join(Message.split(' ')[:-1])
        return check_length_for_tweet(Hash, Message)

    return Hash, Message


def make_a_tweet(Hash, Message):
    """
    Generate a valid tweet using the info passed in.
    """
    return Hash + ': ' + Message


def Tweet(Tweet, revision):
    """
    Tweet the commit message and wrie the revision number to a file.
    """
    # Twitter authentication
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)

    api.update_status(Tweet)

    # store the hash in a file
    with open('.hash', 'w') as f:
        f.write(revision)


def OtherTweets():
    pass


def CheckForNewCommit(Revision):
    """
    Avoid repeating the same tweet by comparing revision numbers.
    Returns True if values are different.
    """
    import os.path as op
    if op.isfile('.hash'):
        with open('.hash', 'r') as f:
            CurrentRev = f.readline()
    else:
        # if the file is not present assume commit is new,
        # set value to zero so function returns True
        CurrentRev = 0
    return CurrentRev != Revision


def Run(repoPath):
    """
    Wrapper to run all of the steps to send out a tweet.
    """
    Hash, Message = ScrapeGIT(repoPath)
    Hash, Message = check_length_for_tweet(Hash, Message)

    if CheckForNewCommit(Hash):
        FinalTweet = make_a_tweet(Hash, Message)
        Tweet(FinalTweet, Hash)
    else:
        # tweet something else?
        pass


if __name__ == "__main__":
    if len(sys.argv) == 2:
        Run(sys.argv[1])
    else:
        sys.exit('%s needs 1 argument:\n\n[1] The path to the git'
                 ' repository\n' % sys.argv[0])
