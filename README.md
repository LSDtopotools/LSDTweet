# LSDTweet

Script that scrapes commit info from a git repo logs, formats the info into
a tweet and then tweets it.
Only works on Python 3.4 and requires Tweepy, GitPython and a secrets.py
file to handle the twitter api keys. It is assumed that the machine this script
is run on has github authentication configured.
Call at the terminal with the path to the repo to tweet from or put it in your
crontab.


SWDG 18/1/17
