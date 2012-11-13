**Twitter Collection Utilities**

ch.py - get historical tweets

dedupl.sh - deduplicate a file of tweets

follow.py - follows a list of users without making twitter suspicious

monitor-timeline.py - get and monitor timeline of a user

monitor-users.py - get and monitor timeline of a list of users

oauth.py - use twitter api as with curl


To add:

How to install (make the packaging)


In order for your scripts to run, you need to authenticate to the Twitter API. This can be done by using the 4 keys Twitter provides you when you register an application. For more information go to https://dev.twitter.com/ To use some script (e.g. follow.py) you need to add the read&write access for your application.

You may have multiple consumers, associated with different accounts/applications. You should store these keys in your home directory in a file named .twittertokens The file should contain the 4 keys separated by a comma in the order:
ConsumerKey,ConsumerSecret,AccessToken,AccessSecret


Generalize redundant functions

