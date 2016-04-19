# Twitter Collection Utilities

*This project is deprecated as it doesn't comply with the new Twitter API guidelines. I have started to recreate the same scripts in a separate project: https://github.com/danielpreotiuc/twitter-collection*

## Description

This is a set of Python scripts that performs some usual data collection tasks from Twitter. This includes continuous crawling of tweets of a list of users or getting all the tweets from a user's timeline.

## Installation

**Packages**

In order for the scripts to run, you need to install some Python packages. These are:

https://github.com/brosner/python-oauth2

**Add the Twitter API Keys (required)**

In order for your scripts to run, you need to authenticate with the Twitter API. This can be done by using the 4 keys Twitter provides you when you register an application. For more information go to https://dev.twitter.com/ To use some scripts (e.g. follow.py) you need to add the read&write access for your application.

You may have multiple consumers, associated with different accounts/applications. You should store these keys in your home directory in a file named .twittertokens The file should contain the 4 keys associated with an application on each line in the following format:
ConsumerKey,ConsumerSecret,AccessToken,AccessSecret

Whenever consumerid is mentioned, it is a integer value k that indicates the credentials on the line k-1 of the file. If not specified, the default consumerid is always 0.

## Scripts

#### dedupl.sh

Deduplicates files of tweets
 
	./dedupl.sh folder

folder - folder of tweet files that need deduplication (relative to script location)

#### follow.py

Follows a list of users from the current account.

	python follow.py userfile consumerid iter wait

userfile - file with the list of user ids, one/line (default 'user-file')

consumerid - number of consumer (see installation section)

iter - number of batches to split the users into (default 10)

wait - wait period between batches of follow requests (default 3600)

#### monitor-location.py

Gets the tweets around a location and updates. Outputs one file/day and archives them using lzop

        python monitor-location.py consumerid latitude longitude radius filenames wait query

consumerid - number of consumer (see installation section)

latitude - latitude of the location

longitude - longitude of the location

radius - radius around the center point (in miles)

filenames - prefix of the files

wait - wait time between calls. Should be adjusted not to cosume too many calls, not less than 10.

query - the query to monitor. If we want as many tweets as possible, use stopwords (e.g. a)

*Example*

        python monitor-location.py 1 -34.5 -58.4 20 buenos-aires 15 a

#### monitor-timeline.py

Gets the timeline of a user and updates every minute. Outputs in a separate file every day.

	python monitor-timeline.py consumerid

consumerid - number of consumer (see installation section)

#### monitor-tt.py

Gets the trending topic at a location and updates every 5 minutes (more often is useless).

        python monitor-tt.py consumerid fout woeid

consumerid - number of consumer (see installation section)

fout - name of output file

woeid - id of location where we want to monitor the trends (defaults to U.K.). List of possible locations taken from: https://dev.twitter.com/docs/api/1.1/get/trends/available

#### monitor-users.py

Gets the historical tweets of a list of users. If given a folder where tweet files of users exists, resumes from the last seen tweet. Suitable for running as a cron job in order to update the tweets at a regular time interval.

        python monitor-users.py userfile consumerid targetfolder

userfile - file with the list of user ids, one/line (default 'user-file')

consumerid - number of consumer (see installation section)

targetfolder - the target folder name (default 'timelines', creates the folder if it doesn't exist)

#### oauth.py

Use twitter api as with curl

	python oauth.py url consumerid

Can be ran as standalone script, without using the Twitter python package

url - url address to the Twitter API

consumerid - number of consumer (see installation section)

*Example*

	python oauth.py https://api.twitter.com/1/statuses/home_timeline.json

#### pp.py 

Pretty print file with json (sorts keys alphabetically)
	
	cat tt-uk | python pp.py | less
		
## Bugs

The scripts were all ran continuously and all the bugs seem to have been eliminated, so the scripts are safe to be run without needing to worry about crashing. However, if you encounter any bugs, please tell me. All the scripts were tested under Unix.

## To add

Generalize some functions

Make package

## Licence


