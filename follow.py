import twitter
import time
import os
import sys
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

CONF_DIR = os.getenv('HOME') # where to find the configuration
CONSUMER = int(sys.argv[1])
tokensIndex = loadTokensIndex(os.sep.join([CONF_DIR,".twittertokens"]))
tokens = tokensIndex[CONSUMER]
c_tw=twitter.Twitter(domain='api.twitter.com',api_version="1",auth=twitter.OAuth(tokens["ATOKEN_KEY"],tokens["ATOKEN_SECRET"],tokens["CLIENT_KEY"],tokens["CLIENT_SECRET"]))

ITER=1
WAIT=10
users = ["lampos","notarealtwitteruser","sinjax","omniphobia","puresock"]
parts = [i for i in xrange(0,len(users),ITER)]

for x in parts:
  part = users[x:x+ITER]
  print "Following %d people" % len(part)
  for person in part:
    try:
      c_tw.friendships.create(screen_name=person)
      print "Following %s" % person
    except twitter.api.TwitterError, e:
      print "Could not add %s" % person
  if x is not parts[-1]:
    print "Waiting %d seconds" % WAIT
    time.sleep(WAIT)
