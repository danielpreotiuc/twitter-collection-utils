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
USER_FILE = (sys.argv[1] if len(sys.argv) >= 2 else "user-file")
CONSUMER = (int(sys.argv[2]) if len(sys.argv) >= 3 else 0)
FOLDER = (sys.argv[3] if len(sys.argv) >= 4 else "timelines")
WAIT_UPDATE = (int(sys.argv[4]) if len(sys.argv) >= 5 else 3600)
if not os.path.exists(FOLDER): os.makedirs(FOLDER)
fuser = open(USER_FILE,'r')
users=[]
sids={}
for line in fuser:
  uname=line.strip()
  users.append(uname)
  sids[uname]=1
  FNAME=FOLDER+"/"+uname
  if (os.path.exists(FNAME)) or (os.path.exists(FNAME+".gz")) or (os.path.exists(FNAME+".lzo")):
    f=open(FNAME)
    l=''
    for line in f:
      l=line
    f.close()    
    sids[uname]=json.loads(l)['id']
             
WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
STEP = 200 # number of tweets retrieved per call; should always be 200 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

c_tw=twitter.Twitter(domain='api.twitter.com',api_version="1",auth=twitter.OAuth(tokens["ATOKEN_KEY"],tokens["ATOKEN_SECRET"],tokens["CLIENT_KEY"],tokens["CLIENT_SECRET"]))
lid=1
while 1==1:
  for user in users:
    print 'Processing user', user
    sid=sids[user]
    try:
      tweets=c_tw.statuses.user_timeline(id=user,count=STEP,since_id=sid)
    except twitter.api.TwitterError, e:
      if e.e.code in (502,503):
        print >> sys.stderr, 'Encountered %i Error, Trying again in %i seconds' % (e.e.code,WAIT_PERIOD)
      if e.e.code==401:
        print >> sys.stderr, 'User %s protects his tweets' % user
        # remove the user for good from our list
        # users[:] = (value for value in users if value != user)
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
          else:
            print >> sys.stderr, 'Other error '+str(e.e.code)
        except:
          print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
      continue
    except e:
      print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
      continue
    print ' has %i new tweets', len(tweets)
    if len(tweets)==0:
      continue
# this is the newset tweet we have, next time download only newer stuff
    sids[user]=tweets[0]['id']
    lid=tweets[len(tweets)-1]['id']
    tlist=tweets
    while lid>sid:
# we have more than STEP tweets in the sleeping time, go back in time until sid and get them
      try:
        tweets=c_tw.statuses.user_timeline(id=user,count=STEP,max_id=lid-1,since_id=sid)
      except twitter.api.TwitterError, e:
        if e.e.code in (502,503):
          print >> sys.stderr, 'Encountered %i Error, Trying again in %i seconds' % (e.e.code,WAIT_PERIOD)
        if e.e.code==401:
          print >> sys.stderr, 'User %s protects his tweets' % user
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
          except:
            print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
        break
      except e:
        print >> sys.stderr, 'Encountered %i, Error %s, Trying again in %i seconds' % (e.e.code,e,WAIT_PERIOD)
        break
      print ' has %i new tweets', len(tweets)
      if len(tweets)==0:
        break
      lid=tweets[len(tweets)-1]['id']
      tlist=tlist+tweets
# print the tweets we got in reverse order so that we mentain the #order of timestamps
    tlist.reverse()
    FNAME=FOLDER+"/"+user
    fout=open(FNAME,'a+')
    for tweet in tlist:
      print >> fout, json.dumps(tweet)
    fout.close()
    time.sleep(WAIT_PERIOD)
  print 'Finished a pass over the list of users, waiting %i seconds' % WAIT_UPDATE
  time.sleep(WAIT_UPDATE)
