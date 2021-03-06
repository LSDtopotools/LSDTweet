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
import random
import git
import sys
import os
import os.path as op
from secrets import *
from datetime import datetime


def ScrapeGIT(repoURL):
    """
    Given a path to a local git repo, return the commit message and hash.
    """
    g = git.cmd.Git(repoURL)
    g.pull()
    Message = (g.log('-1', '--pretty=format:%s'))
    Hash = (g.log('-1', '--pretty=format:%h'))

    return Hash, Message


def reduce_length_for_tweet(Hash, Message, Reduced=False):
    """
    Recursively remove a word from the message until it is small enough to tweet
    Reduced is a boolean testing if the string has been shortened. If it
    has, an ellipsis (…) will be placed at the end of the tweet.
    """
    if len(Hash) + len(Message) > 133:
        # get rid of a word
        Message = ' '.join(Message.split(' ')[:-1])
        Reduced = True
        return reduce_length_for_tweet(Hash, Message, Reduced)

    return Hash, Message, Reduced


def make_a_tweet(Hash, Message, Reduced):
    """
    Generate a valid tweet using the info passed in.
    """
    tweet = Hash + ': ' + Message
    if Reduced:
        tweet += '…'
    return tweet


def ConvertHashToDate(Hash):
    """
    Converts a unix datestamp given in hexadecimal to
    a formatted date dd/mm/YYYY
    """
    return datetime.utcfromtimestamp(int(Hash, 16)).strftime('%d/%m/%Y')


def Tweet(Tweet, Hash=''):
    """
    Tweet the commit message and wrie the revision number to a file.
    """
    # Twitter authentication
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.update_status(Tweet)

    print (Tweet)
    if Hash:
        # store the hash in a file
        path = op.realpath(op.join(os.getcwd(), op.dirname(__file__)))
        with open(op.join(path, '.hash'), 'w') as f:
            f.write(Hash)


def GetRecentTweets():
    """
    Load the most recent tweets from a file.
    """
    path = op.realpath(op.join(os.getcwd(), op.dirname(__file__)))
    recentFile = op.join(path, '.recent')
    if op.isfile(recentFile):
        with open(recentFile, 'r') as f:
            return f.readlines()
    else:
        return ['']


def OtherTweets():
    '''
    Load a random tweet from the file, check its length and if it has been
    recently tweeted.
    '''
    path = op.realpath(op.join(os.getcwd(), op.dirname(__file__)))
    with open(op.join(path, 'Tweets.txt'), 'r') as f:
        Tweets = f.readlines()

    Recent = GetRecentTweets()

    # cycle through random tweets until one meets the criteria.
    while True:
        text = random.choice(Tweets)

        if (text not in Recent) and CheckLength(text):
            break

    return text


def CheckLength(tweet):
    """
    Check the prospective tweet is not too long.
    """
    if len(tweet) > 139:
        return False
    else:
        return True


def WriteRecent(tweet):
    """
    Write the most recent tweet to a file, keeping the n most recent tweets.
    Adds tweet to front of file and pops the oldest recent tweet off the file.
    """
    path = op.realpath(op.join(os.getcwd(), op.dirname(__file__)))
    recentFile = op.join(path, '.recent')
    if op.isfile(recentFile):
        recent = GetRecentTweets()
    else:
        recent = []

    # if the list is longer than 15, remove the last entry and add the tweet
    # otherwise just add the tweet to the list
    # THIS VALUE MUST BE LESS THAN THE NUMBER OF TWEETS IN THE FILE TO AVOID
    # AN INFINITE LOOP
    if len(recent) > 14:
        recent = [''] + recent[:-1]
        recent[0] = tweet
    else:
        recent = [''] + recent[:]
        recent[0] = tweet

    with open(recentFile, 'w') as f:
        for r in recent:
            f.write(r)


def CheckForNewCommit(Hash):
    """
    Avoid repeating the same tweet by comparing hashes.
    Returns True if values are different.
    """
    path = op.realpath(op.join(os.getcwd(), op.dirname(__file__)))
    hashFile = op.join(path, '.hash')
    if op.isfile(hashFile):
        with open(hashFile, 'r') as f:
            CurrentRev = f.readline()
    else:
        # if the file is not present assume commit is new,
        # set value to zero so function returns True
        CurrentRev = '0'

    return CurrentRev != Hash


def Run(repoPath):
    """
    Wrapper to run all of the steps to send out a tweet.
    """
    Hash, Message = ScrapeGIT(repoPath)
    Hash, Message, Reduced = reduce_length_for_tweet(Hash, Message)

    if CheckForNewCommit(Hash):
        FinalTweet = make_a_tweet(Hash, Message, Reduced)
        Tweet(FinalTweet, Hash)
    else:
        # tweet something else?
        tweet = OtherTweets()
        Tweet(tweet)
        WriteRecent(tweet)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        Run(sys.argv[1])
    else:
        sys.exit('%s needs 1 argument:\n\n[1] The path to the git'
                 ' repository\n' % sys.argv[0])
