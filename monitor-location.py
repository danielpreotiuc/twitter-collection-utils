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
CONSUMER = int(sys.argv[1])
LNAME=sys.argv[5]
WAIT_CALL=int(sys.argv[6])
QUERY=sys.argv[7]
GC=sys.argv[2]+","+sys.argv[3]+","+sys.argv[4]+"mi"

WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
# WAIT_CALL = 15 # frequency of checking the timeline (I think it's useless checking more often than 60 seconds)
STEP = 100 # number of tweets retrieved per call; should always be 100 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

sid=1
d=datetime.datetime.now()
da=d.day
FNAME=LNAME+"-"+str(d.year)+'-'+str(d.month)+'-'+str(d.day)
fout=open(FNAME,"w")
while 1==1:
  if not da==datetime.datetime.now().day:
    d=datetime.datetime.now()
    da=d.day   
    fout.close()
    os.system("lzop -9U "+FNAME)
    FNAME=LNAME+"-"+str(d.year)+'-'+str(d.month)+'-'+str(d.day)
    fout=open(FNAME,"w")
  r,c=request('https://api.twitter.com/1.1/search/tweets.json?q='+QUERY+'&count='+str(STEP)+'&geocode='+GC+'&since_id='+str(sid)+'&result_type="recent"')
  st=int(r['status'])
  if st==200:
    t=json.loads(c)
    tlist=t['statuses']
    if len(tlist)==0:
      time.sleep(WAIT_CALL)
      continue
    sid=int(tlist[0]['id_str'])
    tlist.reverse()
    print len(tlist)
    for tweet in tlist:
      print >> fout, json.dumps(tweet)
    time.sleep(WAIT_CALL)    
  elif st==429:
    wait_time=60
    r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
    try:
      rstatus=json.loads(c)
      if int(rstatus['resources']['search']['/search/tweets']['remaining'])==0:
        now=time.time()
        reset=int(rstatus['resources']['search']['/search/tweets']['reset'])
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
    print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
    time.sleep(WAIT_PERIOD)
  tlist=t['statuses']
  if len(tlist)==0:
    time.sleep(WAIT_CALL)
    continue
  sid=int(tlist[0]['id_str'])
  tlist.reverse()
  print len(tlist)
  for tweet in tlist:
    print >> fout, json.dumps(tweet)
    fout.flush()
  time.sleep(WAIT_CALL)
