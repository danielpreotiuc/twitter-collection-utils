#!/usr/bin/env python
# gets the last 3200 tweets of each user

# arg1 is a file with twitter screen names (one user/line), default user-file
# arg2 is a consumer id (so far there are from 0-6), default 0
# arg3 a target folder name for all the files, default timelines
# needs a ~/.twittertokens file

import time
import sys
import twitter
import json
import cPickle as pickle
import os

def loadTokensIndex(loc):
	f = file(loc,"r")
	index = []
	for line in f.readlines():
		if line.startswith("#"): continue
		parts = [x.strip() for x in line.split(",")]
		(consumer_key,consumer_secret,auth_key,auth_secret) = parts
		tokens = dict()
		tokens["CLIENT_KEY"] = consumer_key
		tokens["CLIENT_SECRET"] = consumer_secret
		tokens["ATOKEN_KEY"] = auth_key
		tokens["ATOKEN_SECRET"] = auth_secret

		index = index + [tokens]
	return index

CONF_DIR = os.getenv('HOME') # where to find the configuration
WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
STEP = 200 # number of tweets attempted to be retrieved per call; should always be 200 (maximum)
USER_FILE = (sys.argv[1] if len(sys.argv) >= 2 else "user-file")
CONSUMER = (int(sys.argv[2]) if len(sys.argv) >= 3 else 0)
FOLDER = (sys.argv[3] if len(sys.argv) >= 4 else "timelines")
if not os.path.exists(FOLDER): os.makedirs(FOLDER)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

c_tw=twitter.Twitter(domain='api.twitter.com',api_version="1",auth=twitter.OAuth(tokens["ATOKEN_KEY"],tokens["ATOKEN_SECRET"],tokens["CLIENT_KEY"],tokens["CLIENT_SECRET"]))

fin=open(USER_FILE,'r+')
for user in fin:
  user=user.strip()
  FNAME=FOLDER+"/"+user
  if (os.path.exists(FNAME)) or (os.path.exists(FNAME+".gz")) or (os.path.exists(FNAME+".lzo")):
    print >> sys.stderr, FNAME+'(.gz/.lzo) exists\n'
    continue 
  fout=file(FNAME,'w')
  k=1
  sid=1
  while k>0:
    try:
      tweets=c_tw.statuses.user_timeline(id=user,count=STEP)
      if len(tweets)==0:
        k=0
        continue
      for t in tweets:
        print >> fout, json.dumps(t)
      lid=tweets[len(tweets)-1]['id']
      while 1==1:
        tweets=c_tw.statuses.user_timeline(id=user,count=STEP,max_id=lid-1)
        if len(tweets)==0:
          k=0
          break;
        lid=tweets[len(tweets)-1]['id']
        for t in tweets:
          print >> fout, json.dumps(t)
    except twitter.api.TwitterError, e:
      if e.e.code in (502,503):
        print >> sys.stderr, 'Encountered %i Error, Trying again in %i seconds' % (e.e.code,WAIT_PERIOD)
        time.sleep(WAIT_PERIOD)
        continue
      if e.e.code==401:
        print >> sys.stderr, 'User %s protects his tweets' % user
        k=0
        break
      else:
        try:
          status=c_tw.account.rate_limit_status()
          hits=status['remaining_hits']          
          if hits==0:
            now=time.time()
            reset=status['reset_time_in_seconds']
            SLEEP=reset-now
            print >> sys.stderr, 'Rate limit reached. Trying again in %i seconds' % (SLEEP)
            time.sleep(SLEEP)
            continue        
          else:
            print >> sys.stderr, 'Other error '+str(e.e.code)
            k=0
            continue
        except:
          print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
          time.sleep(WAIT_PERIOD)
          continue
    except e:
      print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
      time.sleep(WAIT_PERIOD)
      continue
  fout.close()
