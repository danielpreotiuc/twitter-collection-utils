import time
import sys
import json
import cPickle as pickle
import os
import datetime  
import oauth2 

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

def request(url):
  try:
    consumer=oauth2.Consumer(key=tokens["CLIENT_KEY"],secret=tokens["CLIENT_SECRET"])
    token=oauth2.Token(key=tokens["ATOKEN_KEY"],secret=tokens["ATOKEN_SECRET"])
    client=oauth2.Client(consumer,token)
    resp,content=client.request(url,method="GET")
  except:
    resp['status']=404;
    content='[]'
  return resp,content

CONF_DIR = os.getenv('HOME') # where to find the configuration
USER_FILE = (sys.argv[1] if len(sys.argv) >= 2 else "user-file")
CONSUMER = (int(sys.argv[2]) if len(sys.argv) >= 3 else 0)
FOLDER = (sys.argv[3] if len(sys.argv) >= 4 else "timelines")
if not os.path.exists(FOLDER): os.makedirs(FOLDER)
fuser = open(USER_FILE,'r')
users=[]
sids={}
for line in fuser:
  uname=line.strip()
  users.append(uname)
  sids[uname]=1
#  this indicates the date I want to start the collection with, for example only stating from 19 Feb 2013
#  sids[uname]=303811956127711232;
  FNAME=FOLDER+"/"+uname
  if (os.path.exists(FNAME)) or (os.path.exists(FNAME+".gz")) or (os.path.exists(FNAME+".lzo")):
    f=open(FNAME)
    l=''
    for line in f:
      l=line
    f.close()    
    try:
      sids[uname]=json.loads(l)['id']
    except:
      pass
             
WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
STEP = 200 # number of tweets retrieved per call; should always be 200 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

lid=1
for user in users:
  print datetime.datetime.now()
  print 'Processing user', user
  sid=sids[user]
  st=0
  sw=0
  while not st==200:
    r,c=request('https://api.twitter.com/1.1/statuses/user_timeline.json?id='+str(user)+'&count='+str(STEP)+'&since_id='+str(sid))
    st=int(r['status'])
    if st==502 or st==503:
      print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
      time.sleep(WAIT_PERIOD)
    elif st==401:
      print 'User %s protects his tweets' % user
      sw=1
      break
    elif st==404:
      print 'Page not found for user %s' % user
      sw=1
      break
    elif st==429:
      wait_time=60
      r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
      try:
        rstatus=json.loads(c)
        if int(rstatus['resources']['statuses']['/statuses/user_timeline']['remaining'])==0:
          now=time.time()
          reset=int(rstatus['resources']['statuses']['/statuses/user_timeline']['reset'])
          print now, reset
          wait_time=reset-now+1
      except:
        pass
      print 'Rate limit reached, waiting %i seconds' % wait_time
      time.sleep(wait_time)
    elif st==400:
      print 'Error %i, waiting 60 seconds' % st
      time.sleep(60)
    else:
      if not st==200:
        print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
        time.sleep(WAIT_PERIOD)
  if sw==1:
    continue
  tweets=json.loads(c)
  print '%s has %i new tweets' % (user,len(tweets))
  if len(tweets)==0:
    continue
# this is the newset tweet we have, next time download only newer stuff
  sids[user]=tweets[0]['id']
  lid=tweets[len(tweets)-1]['id']
  tlist=tweets
  while lid>sid:
# we have more than STEP tweets in the sleeping time, go back in time until sid and get them
    st=0
    sw=0
    while not st==200:
      r,c=request('https://api.twitter.com/1.1/statuses/user_timeline.json?id='+str(user)+'&count='+str(STEP)+'&since_id='+str(sid)+'&max_id='+str(lid-1))
      st=int(r['status'])
      if st==502 or st==503:
        print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
        time.sleep(WAIT_PERIOD)
      elif st==401:
        print 'User %s protects his tweets' % user
        sw=1
        break
      elif st==429:
        wait_time=60
        r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
        try:
          rstatus=json.loads(c)
          if int(rstatus['resources']['statuses']['/statuses/user_timeline']['remaining'])==0:
            now=time.time()
            reset=int(rstatus['resources']['statuses']['/statuses/user_timeline']['reset'])
            print now, reset
            wait_time=reset-now+1
        except:
          pass
        print 'Rate limit reached, waiting %i seconds' % wait_time
        time.sleep(wait_time)      
      elif st==400:
        print 'Error %i, waiting 60 seconds' % st
        time.sleep(60)
      elif st==404:
        print 'Page not found for user %s' % user
        sw=1
        break
      else:
        if not st==200:
          print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
          time.sleep(WAIT_PERIOD)
    if sw==1:
      continue
    tweets=json.loads(c)
    print '%s has %i new tweets' % (user,len(tweets))
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
