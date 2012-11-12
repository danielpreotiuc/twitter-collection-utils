# updates the tweets from a user timeline
# arg1 is the consumer id (so far there are from 0-6)
import time
import sys
import twitter
import json
import cPickle as pickle
import os
import datetime

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
CONSUMER = int(sys.argv[1])

WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
WAIT_CALL = 60 # frequency of checking the timeline (I think it's useless checking more often than 60 seconds)
STEP = 200 # number of tweets retrieved per call; should always be 200 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

c_tw=twitter.Twitter(domain='api.twitter.com',api_version="1",auth=twitter.OAuth(tokens["ATOKEN_KEY"],tokens["ATOKEN_SECRET"],tokens["CLIENT_KEY"],tokens["CLIENT_SECRET"]))

new_sid=1
sid=1
lid=1
d=datetime.datetime.now()
da=d.day
FNAME="TMSORA-"+str(d.year)+'-'+str(d.month)+'-'+str(d.day)
fout=open(FNAME,"w")
while 1==1:
  if not da==datetime.datetime.now().day:
    d=datetime.datetime.now()
    da=d.day   
    fout.close()
    os.system("lzop -9U "+FNAME)
    FNAME="TMSORA-"+str(d.year)+'-'+str(d.month)+'-'+str(d.day)
    fout=open(FNAME,"w")
  try:
    tweets=c_tw.statuses.home_timeline(count=STEP,since_id=sid)
  except twitter.api.TwitterError, e:
    time.sleep(WAIT_PERIOD)
  if len(tweets)==0:
    time.sleep(WAIT_CALL)
    continue
# this is the newset tweet we have, next time download only newer stuff
  new_sid=tweets[0]['id']
  lid=tweets[len(tweets)-1]['id']
  tlist=tweets
  while lid>sid:
# we have more than STEP tweets in the sleeping time, go back in time until sid and get them
    try:
      tweets=c_tw.statuses.home_timeline(count=STEP,max_id=lid-1,since_id=sid)
    except twitter.api.TwitterError, e:
      time.sleep(WAIT_PERIOD)
      break;  
    if len(tweets)==0:
      break
    lid=tweets[len(tweets)-1]['id']
    tlist=tlist+tweets
# print the tweets we got in reverse order so that we mentain the order of timestamps
  tlist.reverse()
  for tweet in tlist:
    print >> fout, json.dumps(tweet)
  sid=new_sid	
  time.sleep(WAIT_PERIOD)
