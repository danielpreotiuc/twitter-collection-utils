import time
import sys
import oauth2
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
CONSUMER = int(sys.argv[1])

WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
WAIT_CALL = 60 # frequency of checking the timeline (I think it's useless checking more often than 60 seconds)
STEP = 200 # number of tweets retrieved per call; should always be 200 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

new_sid=1
sid=1
lid=1
d=datetime.datetime.now()
da=d.day
FNAME=str(d.year)+'-'+str(d.month)+'-'+str(d.day)
fout=open(FNAME,"w")
while 1==1:
  if not da==datetime.datetime.now().day:
    d=datetime.datetime.now()
    da=d.day   
    fout.close()
    os.system("lzop -9U "+FNAME)
    FNAME=str(d.year)+'-'+str(d.month)+'-'+str(d.day)
    fout=open(FNAME,"w")
  print sid
  r,c=request('https://api.twitter.com/1.1/statuses/home_timeline.json?count='+str(STEP)+'&since_id='+str(sid))
  st=int(r['status'])
  if st==200:
    tweets=json.loads(c)
    print len(tweets)
  elif st==429:
    wait_time=60
    r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
    try:
      rstatus=json.loads(c)
      if int(rstatus['resources']['statuses']['/statuses/home_timeline']['remaining'])==0:
        now=time.time()
        reset=int(rstatus['resources']['statuses']['/statuses/home_timeline']['reset'])
        print now, reset
        wait_time=reset-now+1
    except:
      pass
    print 'Rate limit reached, waiting %i seconds' % wait_time
    time.sleep(wait_time)
    continue
  elif st==400:
    print 'Error %i, waiting 60 seconds' % st
    time.sleep(60)
    continue
  else:
    print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
    time.sleep(WAIT_PERIOD)
    continue
  if len(tweets)==0:
    time.sleep(WAIT_CALL)
    continue
# this is the newset tweet we have, next time download only newer stuff
  new_sid=tweets[0]['id']
  lid=tweets[len(tweets)-1]['id']-1
  tlist=tweets
  while lid>sid:
# we have more than STEP tweets in the sleeping time, go back in time until sid and get them
    r,c=request('https://api.twitter.com/1.1/statuses/home_timeline.json?count='+str(STEP)+'&max_id='+str(lid)+'&since_id='+str(sid))
    st=int(r['status'])
    if st==200:
      tweets=json.loads(c)
      print len(tweets)
    elif st==429:
      wait_time=60
      r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
      try:
        rstatus=json.loads(c)
        if int(rstatus['resources']['statuses']['/statuses/home_timeline']['remaining'])==0:
          now=time.time()
          reset=int(rstatus['resources']['statuses']['/statuses/home_timeline']['reset'])
          print now, reset
          wait_time=reset-now+1
      except:
        pass
      print 'Rate limit reached, waiting %i seconds' % wait_time
      time.sleep(wait_time)
      break
    elif st==400:
      print 'Error %i, waiting 60 seconds' % st
      time.sleep(60)
      break
    else:
      print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
      time.sleep(WAIT_PERIOD)
      break
    if len(tweets)==0:
      break
    lid=tweets[len(tweets)-1]['id']-1
    tlist=tlist+tweets
# print the tweets we got in reverse order so that we mentain the order of timestamps
  tlist.reverse()
  for tweet in tlist:
    print >> fout, json.dumps(tweet)
  sid=new_sid	
  time.sleep(WAIT_CALL)
