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
tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]
WAIT_PERIOD=2 
FNAME=str(sys.argv[2])
LOC_ID = (sys.argv[3] if len(sys.argv) >= 4 else "23424975")
# defaults to U.K.

fout=open(FNAME,'a')
while 1==1:
  r,c=request('https://api.twitter.com/1.1/trends/place.json?id='+LOC_ID)
  st=int(r['status'])
  if st==502 or st==503:
    print 'Error %i' % st
    time.sleep(WAIT_PERIOD)
  elif st==401:
    print '401 error'
    time.sleep(WAIT_PERIOD)
  elif st==404:
    print 'Page not found'
    time.sleep(WAIT_PERIOD)
  elif st==429:
    r,c=request('https://api.twitter.com/1.1/application/rate_limit_status.json')
    try:
      rstatus=json.loads(c)
      if int(rstatus['resources']['trends']['/trends/place']['remaining'])==0:
        now=time.time()
        reset=int(rstatus['resources']['trends']['/trends/place']['reset'])
        print now, reset
        wait_time=reset-now+1
    except:
      pass
    print 'Rate limit reached, waiting %i seconds' % wait_time
    time.sleep(wait_time)
  elif st==400:
    print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
    time.sleep(WAIT_PERIOD)
  else:
    if not st==200:
      print 'Error %i, waiting %i seconds' % (st,WAIT_PERIOD)
      time.sleep(WAIT_PERIOD)
    else:
      fout.write(c+'\n')
      fout.flush()
  time.sleep(300-1)
