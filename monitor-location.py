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
LNAME=sys.argv[5]
WAIT_CALL=int(sys.argv[6])
QUERY=sys.argv[7]
GC=sys.argv[2]+","+sys.argv[3]+","+sys.argv[4]+"mi"

WAIT_PERIOD = 2 # time until retry for a failed Twitter API call
# WAIT_CALL = 15 # frequency of checking the timeline (I think it's useless checking more often than 60 seconds)
STEP = 100 # number of tweets retrieved per call; should always be 100 (maximum)

tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]

c_tw=twitter.Twitter(domain='api.twitter.com',api_version="1.1",auth=twitter.OAuth(tokens["ATOKEN_KEY"],tokens["ATOKEN_SECRET"],tokens["CLIENT_KEY"],tokens["CLIENT_SECRET"]))

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
  try:
    t=c_tw.search.tweets(q=QUERY,count=STEP,geocode=GC,since_id=sid,result_type="recent")
  except twitter.api.TwitterError, e:
    time.sleep(WAIT_PERIOD)
  except:
    continue
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
